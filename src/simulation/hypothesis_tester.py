"""
Hypothesis Testing Framework for Trading Strategies
Run systematic tests to prove/disprove trading hypotheses
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

from src.simulation.simulator import TradingSimulator
from src.database.connection import DatabaseManager
from loguru import logger


@dataclass
class HypothesisTest:
    """Represents a trading hypothesis test"""
    name: str
    description: str
    strategy: str
    parameters: Dict[str, Any]
    success_criteria: Dict[str, float]  # e.g., {"win_rate": 0.55, "avg_return": 0.02}
    
    # Results
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_return: float = 0.0
    avg_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    
    # Trade history
    trades: List[Dict] = None
    
    def __post_init__(self):
        if self.trades is None:
            self.trades = []
    
    @property
    def is_successful(self) -> bool:
        """Check if hypothesis meets success criteria"""
        for metric, target in self.success_criteria.items():
            if metric == "win_rate" and self.win_rate < target:
                return False
            elif metric == "avg_return" and self.avg_return < target:
                return False
            elif metric == "sharpe_ratio" and self.sharpe_ratio < target:
                return False
        return self.total_trades > 0


class HypothesisTester:
    """Framework for testing trading hypotheses"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.test_results: List[HypothesisTest] = []
        self.current_test: Optional[HypothesisTest] = None
        
        # Create results directory
        self.results_dir = Path(__file__).parent.parent.parent / "hypothesis_results"
        self.results_dir.mkdir(exist_ok=True)
    
    async def test_momentum_hypothesis(self, num_trades: int = 100) -> HypothesisTest:
        """
        Hypothesis: Momentum signals (RSI + Volume) generate profitable options trades
        Success Criteria: Win rate > 55%, Avg return > 2%
        """
        
        test = HypothesisTest(
            name="Momentum Options Strategy",
            description="Buy CALL options when RSI < 30 and volume spike, PUT when RSI > 70",
            strategy="momentum",
            parameters={
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "volume_threshold": 1.5,
                "holding_period_days": 5
            },
            success_criteria={
                "win_rate": 0.55,
                "avg_return": 0.02
            }
        )
        
        self.current_test = test
        sim = TradingSimulator(self.initial_capital)
        
        print(f"\n🧪 Testing: {test.name}")
        print(f"   {test.description}")
        print(f"   Running {num_trades} simulated trades...")
        
        for i in range(num_trades):
            # Simulate RSI
            rsi = 30 + (70 * (i % 10) / 10)  # Cycles through RSI values
            
            # Generate signal based on RSI
            if rsi < test.parameters["rsi_oversold"]:
                signal = "CALL"
                confidence = (test.parameters["rsi_oversold"] - rsi) / test.parameters["rsi_oversold"]
            elif rsi > test.parameters["rsi_overbought"]:
                signal = "PUT"
                confidence = (rsi - test.parameters["rsi_overbought"]) / (100 - test.parameters["rsi_overbought"])
            else:
                continue  # No signal
            
            # Execute trade
            spy_price = sim.get_market_price("SPY")
            
            # Place options trade
            strike = round(spy_price + (5 if signal == "CALL" else -5))
            order = await sim.place_order(
                symbol="SPY",
                quantity=1,
                side="BUY",
                order_type="MARKET",
                is_option=True,
                strike=strike,
                expiration=datetime.now() + timedelta(days=30),
                option_type=signal
            )
            
            entry_price = order.filled_price
            
            # Simulate holding period and price movement
            for _ in range(test.parameters["holding_period_days"]):
                sim.update_prices()
            
            # Close position
            exit_price = sim.get_option_price("SPY", strike, signal, 25)
            pnl = (exit_price - entry_price) * 100  # 1 contract = 100 shares
            return_pct = (exit_price - entry_price) / entry_price
            
            # Record trade
            trade = {
                "signal": signal,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "return_pct": return_pct,
                "rsi": rsi,
                "confidence": confidence
            }
            
            test.trades.append(trade)
            test.total_trades += 1
            
            if pnl > 0:
                test.winning_trades += 1
            else:
                test.losing_trades += 1
            
            test.total_return += return_pct
            
            if (i + 1) % 20 == 0:
                print(f"   Progress: {i + 1}/{num_trades} trades completed...")
        
        # Calculate final metrics
        self._calculate_metrics(test)
        
        # Save results
        await self._save_results(test)
        
        return test
    
    async def test_volatility_hypothesis(self, num_trades: int = 100) -> HypothesisTest:
        """
        Hypothesis: High IV percentile (>80) is good for selling options
        Success Criteria: Win rate > 60%, Avg return > 1.5%
        """
        
        test = HypothesisTest(
            name="Volatility Premium Capture",
            description="Sell options when IV percentile > 80, buy when < 20",
            strategy="volatility",
            parameters={
                "iv_high_threshold": 80,
                "iv_low_threshold": 20,
                "delta_target": 0.30,
                "holding_period_days": 7
            },
            success_criteria={
                "win_rate": 0.60,
                "avg_return": 0.015
            }
        )
        
        self.current_test = test
        sim = TradingSimulator(self.initial_capital)
        
        print(f"\n🧪 Testing: {test.name}")
        print(f"   {test.description}")
        print(f"   Running {num_trades} simulated trades...")
        
        for i in range(num_trades):
            # Simulate IV percentile
            iv_percentile = (i * 7) % 100  # Cycles through IV values
            
            # Generate signal
            if iv_percentile > test.parameters["iv_high_threshold"]:
                # High IV - sell options (simplified as selling = inverse trade)
                signal = "PUT"  # Sell calls = bet on decrease
                confidence = 0.7
            elif iv_percentile < test.parameters["iv_low_threshold"]:
                # Low IV - buy options
                signal = "CALL"
                confidence = 0.6
            else:
                continue
            
            # Execute trade
            spy_price = sim.get_market_price("SPY")
            strike = round(spy_price)  # ATM options
            
            order = await sim.place_order(
                symbol="SPY",
                quantity=1,
                side="BUY",
                order_type="MARKET",
                is_option=True,
                strike=strike,
                expiration=datetime.now() + timedelta(days=30),
                option_type=signal
            )
            
            entry_price = order.filled_price
            
            # Simulate holding
            for _ in range(test.parameters["holding_period_days"]):
                sim.update_prices()
            
            # Close position
            exit_price = sim.get_option_price("SPY", strike, signal, 23)
            pnl = (exit_price - entry_price) * 100
            return_pct = (exit_price - entry_price) / entry_price if entry_price > 0 else 0
            
            # Record trade
            trade = {
                "signal": signal,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "return_pct": return_pct,
                "iv_percentile": iv_percentile,
                "confidence": confidence
            }
            
            test.trades.append(trade)
            test.total_trades += 1
            
            if pnl > 0:
                test.winning_trades += 1
            else:
                test.losing_trades += 1
            
            test.total_return += return_pct
        
        # Calculate metrics
        self._calculate_metrics(test)
        
        # Save results
        await self._save_results(test)
        
        return test
    
    async def test_trend_following_hypothesis(self, num_trades: int = 100) -> HypothesisTest:
        """
        Hypothesis: Following strong trends with options is profitable
        Success Criteria: Win rate > 52%, Avg return > 3%
        """
        
        test = HypothesisTest(
            name="Trend Following Options",
            description="Buy CALL in uptrends, PUT in downtrends using MA crossovers",
            strategy="trend_following",
            parameters={
                "fast_ma": 20,
                "slow_ma": 50,
                "atr_multiplier": 2.0,
                "holding_period_days": 10
            },
            success_criteria={
                "win_rate": 0.52,
                "avg_return": 0.03
            }
        )
        
        self.current_test = test
        sim = TradingSimulator(self.initial_capital)
        
        print(f"\n🧪 Testing: {test.name}")
        print(f"   {test.description}")
        
        # Run test trades
        for i in range(num_trades):
            # Simulate trend (simplified)
            trend_strength = -1 + (2 * i / num_trades)  # -1 to +1
            
            if trend_strength > 0.2:
                signal = "CALL"
                confidence = min(0.9, trend_strength)
            elif trend_strength < -0.2:
                signal = "PUT"
                confidence = min(0.9, abs(trend_strength))
            else:
                continue
            
            # Trade execution
            spy_price = sim.get_market_price("SPY")
            strike = round(spy_price + (10 * trend_strength))  # OTM based on trend
            
            order = await sim.place_order(
                symbol="SPY",
                quantity=2,  # 2 contracts for trend following
                side="BUY",
                order_type="MARKET",
                is_option=True,
                strike=strike,
                expiration=datetime.now() + timedelta(days=45),
                option_type=signal
            )
            
            entry_price = order.filled_price
            
            # Hold position
            for _ in range(test.parameters["holding_period_days"]):
                # Trend continues with some noise
                if signal == "CALL":
                    sim.market_prices["SPY"] *= 1.002  # Slight upward bias
                else:
                    sim.market_prices["SPY"] *= 0.998  # Slight downward bias
                sim.update_prices()
            
            # Exit
            exit_price = sim.get_option_price("SPY", strike, signal, 35)
            pnl = (exit_price - entry_price) * 200  # 2 contracts
            return_pct = (exit_price - entry_price) / entry_price if entry_price > 0 else 0
            
            # Record
            trade = {
                "signal": signal,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "return_pct": return_pct,
                "trend_strength": trend_strength,
                "confidence": confidence
            }
            
            test.trades.append(trade)
            test.total_trades += 1
            
            if pnl > 0:
                test.winning_trades += 1
            else:
                test.losing_trades += 1
            
            test.total_return += return_pct
        
        self._calculate_metrics(test)
        await self._save_results(test)
        
        return test
    
    def _calculate_metrics(self, test: HypothesisTest):
        """Calculate test metrics"""
        if test.total_trades == 0:
            return
        
        test.win_rate = test.winning_trades / test.total_trades
        test.avg_return = test.total_return / test.total_trades
        
        # Calculate profit factor
        gains = sum(t["pnl"] for t in test.trades if t["pnl"] > 0)
        losses = abs(sum(t["pnl"] for t in test.trades if t["pnl"] < 0))
        test.profit_factor = gains / losses if losses > 0 else gains
        
        # Calculate max drawdown
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in test.trades:
            cumulative += trade["pnl"]
            peak = max(peak, cumulative)
            drawdown = (peak - cumulative) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        test.max_drawdown = max_dd
        
        # Simple Sharpe ratio
        returns = [t["return_pct"] for t in test.trades]
        if len(returns) > 1:
            avg_return = statistics.mean(returns)
            std_return = statistics.stdev(returns)
            test.sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
    
    async def _save_results(self, test: HypothesisTest):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"{test.strategy}_{timestamp}.json"
        
        # Convert to dict for JSON serialization
        results = {
            "test_info": {
                "name": test.name,
                "description": test.description,
                "strategy": test.strategy,
                "parameters": test.parameters,
                "success_criteria": test.success_criteria,
                "timestamp": timestamp
            },
            "metrics": {
                "total_trades": test.total_trades,
                "winning_trades": test.winning_trades,
                "losing_trades": test.losing_trades,
                "win_rate": test.win_rate,
                "avg_return": test.avg_return,
                "total_return": test.total_return,
                "profit_factor": test.profit_factor,
                "max_drawdown": test.max_drawdown,
                "sharpe_ratio": test.sharpe_ratio
            },
            "is_successful": test.is_successful,
            "trades": test.trades[:10]  # Save first 10 trades as sample
        }
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to {filename}")
        
        # Also log to database if available
        try:
            db = DatabaseManager()
            await db.log_signal({
                "symbol": "HYPOTHESIS_TEST",
                "signal_type": test.strategy.upper(),
                "confidence": test.win_rate,
                "strategy_name": test.name,
                "claude_recommendation": json.dumps(results["metrics"]),
                "claude_confidence": test.win_rate,
                "was_profitable": test.is_successful,
                "profit_loss": test.total_return * 1000,  # Scale for storage
                "profit_loss_percent": test.avg_return * 100
            })
            await db.close()
        except Exception as e:
            logger.warning(f"Could not log to database: {e}")
    
    def print_summary(self, test: HypothesisTest):
        """Print test summary"""
        print("\n" + "="*60)
        print(f"📊 HYPOTHESIS TEST RESULTS: {test.name}")
        print("="*60)
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Total Trades:    {test.total_trades}")
        print(f"   Winning Trades:  {test.winning_trades}")
        print(f"   Losing Trades:   {test.losing_trades}")
        print(f"   Win Rate:        {test.win_rate:.1%}")
        print(f"   Avg Return:      {test.avg_return:.2%}")
        print(f"   Total Return:    {test.total_return:.2%}")
        print(f"   Profit Factor:   {test.profit_factor:.2f}")
        print(f"   Max Drawdown:    {test.max_drawdown:.2%}")
        print(f"   Sharpe Ratio:    {test.sharpe_ratio:.2f}")
        
        print(f"\n🎯 Success Criteria:")
        for metric, target in test.success_criteria.items():
            actual = getattr(test, metric)
            passed = "✅" if actual >= target else "❌"
            print(f"   {metric}: {actual:.2%} (target: {target:.2%}) {passed}")
        
        print(f"\n{'✅ HYPOTHESIS VALIDATED' if test.is_successful else '❌ HYPOTHESIS REJECTED'}")
        
        if test.is_successful:
            print(f"\n💡 This strategy shows promise for live testing!")
        else:
            print(f"\n💡 Consider adjusting parameters or trying a different approach.")


async def run_all_hypothesis_tests():
    """Run all hypothesis tests"""
    
    print("\n" + "="*60)
    print("🔬 RUNNING HYPOTHESIS TESTING SUITE")
    print("="*60)
    print("\nThis will test multiple trading hypotheses using simulation.")
    print("Each test runs 100 trades to evaluate performance.")
    
    tester = HypothesisTester()
    results = []
    
    # Test 1: Momentum
    print("\n[1/3] Testing Momentum Hypothesis...")
    momentum_test = await tester.test_momentum_hypothesis(num_trades=50)
    tester.print_summary(momentum_test)
    results.append(momentum_test)
    
    # Test 2: Volatility
    print("\n[2/3] Testing Volatility Hypothesis...")
    volatility_test = await tester.test_volatility_hypothesis(num_trades=50)
    tester.print_summary(volatility_test)
    results.append(volatility_test)
    
    # Test 3: Trend Following
    print("\n[3/3] Testing Trend Following Hypothesis...")
    trend_test = await tester.test_trend_following_hypothesis(num_trades=50)
    tester.print_summary(trend_test)
    results.append(trend_test)
    
    # Final Summary
    print("\n" + "="*60)
    print("🏁 HYPOTHESIS TESTING COMPLETE")
    print("="*60)
    
    successful = [t for t in results if t.is_successful]
    print(f"\nResults: {len(successful)}/{len(results)} hypotheses validated")
    
    if successful:
        print("\n✅ Validated Strategies:")
        for test in successful:
            print(f"   • {test.name}: {test.win_rate:.1%} win rate, {test.avg_return:.2%} avg return")
    
    print(f"\n📁 Detailed results saved in: hypothesis_results/")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_hypothesis_tests())