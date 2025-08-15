"""
Options Trading Strategy Engine
Implements various options strategies with risk management
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
import numpy as np


@dataclass
class OptionSignal:
    """Trading signal for options"""
    ticker: str
    option_type: str  # CALL or PUT
    strike_price: float
    expiration_date: datetime
    action: str  # BUY or SELL
    quantity: int
    confidence: float
    strategy_name: str
    reason: str
    risk_score: float
    expected_return: float
    max_loss: float


@dataclass
class MarketConditions:
    """Current market conditions"""
    vix: float  # Volatility index
    spy_trend: str  # BULLISH, BEARISH, NEUTRAL
    market_volume: str  # HIGH, NORMAL, LOW
    earnings_season: bool
    fed_meeting_week: bool
    options_volume_ratio: float  # Put/Call ratio


class BaseStrategy:
    """Base class for all options strategies"""
    
    def __init__(self, name: str, risk_level: str = "MEDIUM"):
        self.name = name
        self.risk_level = risk_level
        self.min_confidence = 0.7
        self.max_position_size = 0.1  # Max 10% of portfolio per position
        
    async def evaluate(
        self,
        ticker: str,
        current_price: float,
        market_conditions: MarketConditions,
        signals: List[Dict]
    ) -> Optional[OptionSignal]:
        """Evaluate if strategy should generate a signal"""
        raise NotImplementedError
        
    def calculate_strike(
        self,
        current_price: float,
        option_type: str,
        otm_percentage: float = 0.02
    ) -> float:
        """Calculate appropriate strike price"""
        if option_type == "CALL":
            return round(current_price * (1 + otm_percentage), 2)
        else:  # PUT
            return round(current_price * (1 - otm_percentage), 2)
            
    def calculate_expiration(self, days_out: int = 30) -> datetime:
        """Calculate options expiration date (next Friday)"""
        target = datetime.now() + timedelta(days=days_out)
        # Find next Friday
        days_ahead = 4 - target.weekday()  # Friday is 4
        if days_ahead <= 0:
            days_ahead += 7
        return target + timedelta(days=days_ahead)


class MomentumStrategy(BaseStrategy):
    """Momentum-based options strategy"""
    
    def __init__(self):
        super().__init__("Momentum Options", "MEDIUM")
        
    async def evaluate(
        self,
        ticker: str,
        current_price: float,
        market_conditions: MarketConditions,
        signals: List[Dict]
    ) -> Optional[OptionSignal]:
        """Generate signal based on momentum indicators"""
        
        # Count bullish vs bearish signals
        bullish_count = sum(1 for s in signals if s.get("signal_type") == "BULLISH")
        bearish_count = sum(1 for s in signals if s.get("signal_type") == "BEARISH")
        
        if not signals:
            return None
            
        # Calculate confidence
        total_signals = len(signals)
        if bullish_count > bearish_count * 1.5:
            confidence = bullish_count / total_signals
            option_type = "CALL"
            reason = f"Strong bullish momentum ({bullish_count}/{total_signals} signals)"
        elif bearish_count > bullish_count * 1.5:
            confidence = bearish_count / total_signals
            option_type = "PUT"
            reason = f"Strong bearish momentum ({bearish_count}/{total_signals} signals)"
        else:
            return None  # No clear direction
            
        if confidence < self.min_confidence:
            return None
            
        # Adjust for market conditions
        if market_conditions.vix > 30:
            confidence *= 0.8  # Reduce confidence in high volatility
            
        # Generate signal
        return OptionSignal(
            ticker=ticker,
            option_type=option_type,
            strike_price=self.calculate_strike(current_price, option_type),
            expiration_date=self.calculate_expiration(30),
            action="BUY",
            quantity=1,  # Will be adjusted by position sizing
            confidence=confidence,
            strategy_name=self.name,
            reason=reason,
            risk_score=0.5,
            expected_return=0.15,
            max_loss=1.0  # 100% for long options
        )


class VolatilityStrategy(BaseStrategy):
    """Volatility-based options strategy"""
    
    def __init__(self):
        super().__init__("Volatility Play", "HIGH")
        
    async def evaluate(
        self,
        ticker: str,
        current_price: float,
        market_conditions: MarketConditions,
        signals: List[Dict]
    ) -> Optional[OptionSignal]:
        """Generate signal based on volatility conditions"""
        
        # High VIX favors buying options
        if market_conditions.vix > 25:
            # Look for directional bias
            sentiment_sum = sum(s.get("sentiment", 0) for s in signals)
            
            if abs(sentiment_sum) < 0.3:
                return None  # No clear direction
                
            option_type = "CALL" if sentiment_sum > 0 else "PUT"
            confidence = min(0.9, market_conditions.vix / 40)  # Higher VIX = higher confidence
            
            return OptionSignal(
                ticker=ticker,
                option_type=option_type,
                strike_price=self.calculate_strike(current_price, option_type, 0.03),
                expiration_date=self.calculate_expiration(45),  # Longer expiration for volatility
                action="BUY",
                quantity=1,
                confidence=confidence,
                strategy_name=self.name,
                reason=f"High volatility play (VIX={market_conditions.vix:.1f})",
                risk_score=0.7,
                expected_return=0.25,
                max_loss=1.0
            )
        
        return None


class HedgeStrategy(BaseStrategy):
    """Protective hedge strategy using puts"""
    
    def __init__(self):
        super().__init__("Protective Hedge", "LOW")
        
    async def evaluate(
        self,
        ticker: str,
        current_price: float,
        market_conditions: MarketConditions,
        signals: List[Dict]
    ) -> Optional[OptionSignal]:
        """Generate hedge signals for portfolio protection"""
        
        # Hedge when market shows weakness
        if (market_conditions.spy_trend == "BEARISH" or 
            market_conditions.vix > 20 or
            market_conditions.options_volume_ratio > 1.2):
            
            confidence = 0.8
            
            return OptionSignal(
                ticker="SPY",  # Always hedge with SPY puts
                option_type="PUT",
                strike_price=self.calculate_strike(current_price, "PUT", 0.02),
                expiration_date=self.calculate_expiration(30),
                action="BUY",
                quantity=1,
                confidence=confidence,
                strategy_name=self.name,
                reason="Portfolio protection hedge",
                risk_score=0.3,  # Low risk as it's insurance
                expected_return=-0.5,  # Expect to lose on hedge
                max_loss=1.0
            )
        
        return None


class CreditSpreadStrategy(BaseStrategy):
    """Credit spread strategy for income generation"""
    
    def __init__(self):
        super().__init__("Credit Spread", "MEDIUM")
        
    async def evaluate(
        self,
        ticker: str,
        current_price: float,
        market_conditions: MarketConditions,
        signals: List[Dict]
    ) -> Optional[OptionSignal]:
        """Generate credit spread signals"""
        
        # Best in low volatility, trending markets
        if market_conditions.vix < 20 and market_conditions.spy_trend != "NEUTRAL":
            
            # Bull put spread in uptrend, bear call spread in downtrend
            if market_conditions.spy_trend == "BULLISH":
                option_type = "PUT"
                action = "SELL"  # Sell put spread
                reason = "Bull put spread in uptrend"
            else:
                option_type = "CALL"
                action = "SELL"  # Sell call spread
                reason = "Bear call spread in downtrend"
            
            return OptionSignal(
                ticker=ticker,
                option_type=option_type,
                strike_price=self.calculate_strike(current_price, option_type, 0.05),
                expiration_date=self.calculate_expiration(45),
                action=action,
                quantity=1,
                confidence=0.75,
                strategy_name=self.name,
                reason=reason,
                risk_score=0.4,
                expected_return=0.08,
                max_loss=0.5  # Defined risk spread
            )
        
        return None


class OptionsStrategyEngine:
    """Main engine that coordinates all strategies"""
    
    def __init__(self):
        self.strategies = [
            MomentumStrategy(),
            VolatilityStrategy(),
            HedgeStrategy(),
            CreditSpreadStrategy()
        ]
        self.position_limits = {
            "max_positions": 10,
            "max_per_ticker": 3,
            "max_portfolio_risk": 0.3  # 30% max risk
        }
        
    async def analyze_opportunity(
        self,
        ticker: str,
        current_price: float,
        market_data: Dict[str, Any],
        whatsapp_signals: List[Dict],
        news_signals: List[Dict]
    ) -> List[OptionSignal]:
        """Analyze trading opportunity across all strategies"""
        
        # Prepare market conditions
        market_conditions = self._extract_market_conditions(market_data)
        
        # Combine all signals
        all_signals = whatsapp_signals + news_signals
        
        # Evaluate each strategy
        signals = []
        for strategy in self.strategies:
            try:
                signal = await strategy.evaluate(
                    ticker,
                    current_price,
                    market_conditions,
                    all_signals
                )
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}")
                
        # Filter and rank signals
        return self._filter_signals(signals)
        
    def _extract_market_conditions(self, market_data: Dict) -> MarketConditions:
        """Extract market conditions from data"""
        return MarketConditions(
            vix=market_data.get("vix", 16.0),
            spy_trend=market_data.get("spy_trend", "NEUTRAL"),
            market_volume=market_data.get("volume", "NORMAL"),
            earnings_season=market_data.get("earnings_season", False),
            fed_meeting_week=market_data.get("fed_meeting", False),
            options_volume_ratio=market_data.get("put_call_ratio", 1.0)
        )
        
    def _filter_signals(self, signals: List[OptionSignal]) -> List[OptionSignal]:
        """Filter and prioritize signals"""
        
        if not signals:
            return []
            
        # Sort by confidence and expected return
        signals.sort(
            key=lambda x: x.confidence * x.expected_return,
            reverse=True
        )
        
        # Apply risk filters
        filtered = []
        total_risk = 0.0
        ticker_counts = {}
        
        for signal in signals:
            # Check position limits
            ticker_counts[signal.ticker] = ticker_counts.get(signal.ticker, 0) + 1
            
            if (len(filtered) < self.position_limits["max_positions"] and
                ticker_counts[signal.ticker] <= self.position_limits["max_per_ticker"] and
                total_risk + signal.risk_score * 0.1 <= self.position_limits["max_portfolio_risk"]):
                
                filtered.append(signal)
                total_risk += signal.risk_score * 0.1
                
        return filtered
        
    async def calculate_position_size(
        self,
        signal: OptionSignal,
        portfolio_value: float,
        current_positions: Dict
    ) -> int:
        """Calculate appropriate position size"""
        
        # Kelly Criterion simplified
        kelly_fraction = (signal.expected_return * signal.confidence) / signal.max_loss
        kelly_fraction = min(0.25, kelly_fraction)  # Cap at 25%
        
        # Adjust for existing positions
        existing_exposure = sum(
            p.get("value", 0) for p in current_positions.values()
            if p.get("ticker") == signal.ticker
        )
        
        available_capital = portfolio_value * kelly_fraction
        available_capital -= existing_exposure
        
        # Assume $100 per contract for simplicity
        contracts = max(1, int(available_capital / 100))
        
        # Apply limits
        return min(contracts, 10)  # Max 10 contracts per trade
        
    def generate_risk_report(self, signals: List[OptionSignal]) -> Dict:
        """Generate risk analysis report"""
        
        if not signals:
            return {"status": "No active signals"}
            
        total_risk = sum(s.risk_score for s in signals) / len(signals)
        max_portfolio_loss = sum(s.max_loss * s.quantity * 100 for s in signals)
        expected_return = sum(s.expected_return * s.confidence for s in signals) / len(signals)
        
        return {
            "total_signals": len(signals),
            "average_risk_score": round(total_risk, 2),
            "max_portfolio_loss": round(max_portfolio_loss, 2),
            "expected_return": round(expected_return * 100, 1),  # As percentage
            "risk_reward_ratio": round(expected_return / total_risk, 2) if total_risk > 0 else 0,
            "strategies_used": list(set(s.strategy_name for s in signals)),
            "tickers": list(set(s.ticker for s in signals))
        }


# Example usage
async def test_strategy_engine():
    """Test the strategy engine"""
    
    engine = OptionsStrategyEngine()
    
    # Mock data
    market_data = {
        "vix": 18.5,
        "spy_trend": "BULLISH",
        "volume": "HIGH",
        "put_call_ratio": 0.8
    }
    
    whatsapp_signals = [
        {"signal_type": "BULLISH", "sentiment": 0.7, "ticker": "AAPL"},
        {"signal_type": "BULLISH", "sentiment": 0.5, "ticker": "AAPL"}
    ]
    
    news_signals = [
        {"signal_type": "BULLISH", "sentiment": 0.6, "ticker": "AAPL"}
    ]
    
    # Analyze
    signals = await engine.analyze_opportunity(
        ticker="AAPL",
        current_price=175.50,
        market_data=market_data,
        whatsapp_signals=whatsapp_signals,
        news_signals=news_signals
    )
    
    # Generate report
    risk_report = engine.generate_risk_report(signals)
    
    print("\n" + "="*60)
    print("OPTIONS STRATEGY ENGINE TEST")
    print("="*60)
    
    for signal in signals:
        print(f"\n📊 Signal: {signal.strategy_name}")
        print(f"   Ticker: {signal.ticker}")
        print(f"   Type: {signal.option_type}")
        print(f"   Strike: ${signal.strike_price}")
        print(f"   Action: {signal.action}")
        print(f"   Confidence: {signal.confidence:.1%}")
        print(f"   Reason: {signal.reason}")
    
    print(f"\n📈 Risk Report:")
    for key, value in risk_report.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_strategy_engine())