"""
Main Trading Bot Entry Point
Coordinates all components and executes trading logic
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database.supabase_client import DatabaseManager as SupabaseClient
from execution.alpaca_client import AlpacaOptionsClient as AlpacaClient
from simulation.simulator import TradingSimulator
from strategies.options_strategy import OptionsStrategyEngine
from ai.claude_decision_maker import ClaudeDecisionMaker, TradingContext
from data_sources.whatsapp_collector import WhatsAppAnalyzer
from monitoring.monitor import TradingMonitor


class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, mode: str = "simulation"):
        """
        Initialize trading bot
        
        Args:
            mode: "simulation", "paper", or "live"
        """
        self.mode = mode
        self.running = False
        
        # Initialize components
        logger.info(f"Initializing Trading Bot in {mode} mode")
        
        # Database
        self.db = SupabaseClient()
        
        # Execution layer
        if mode == "simulation":
            self.executor = TradingSimulator()
            logger.info("Using simulated trading")
        else:
            self.executor = AlpacaClient()
            logger.info(f"Using Alpaca {'paper' if mode == 'paper' else 'live'} trading")
            
        # Strategy engine
        self.strategy_engine = OptionsStrategyEngine()
        
        # AI decision maker (optional)
        self.ai_enabled = os.getenv("ANTHROPIC_API_KEY") is not None
        if self.ai_enabled:
            self.decision_maker = ClaudeDecisionMaker()
            logger.info("Claude AI decision maker enabled")
        else:
            logger.warning("Claude AI disabled (no API key)")
            
        # Data sources
        self.whatsapp_analyzer = WhatsAppAnalyzer()
        
        # Monitoring
        self.monitor = TradingMonitor()
        
        # State
        self.portfolio_state = {
            "total_value": 100000,
            "cash": 100000,
            "positions": {},
            "position_count": 0
        }
        
    async def initialize(self) -> bool:
        """Initialize all components"""
        
        try:
            # Initialize database
            try:
                await self.db.initialize_database()
            except AttributeError:
                # DatabaseManager doesn't have initialize_database method yet
                logger.info("Database initialization skipped (method not implemented)")
                
            # Connect to Alpaca if not simulation
            if self.mode != "simulation":
                connected = await self.executor.connect()
                if not connected:
                    logger.error("Failed to connect to Alpaca")
                    return False
                    
            # Check system health
            health = await self.monitor.check_system_health()
            logger.info(f"System health check: {health.api_status}")
            
            logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
            
    async def run_cycle(self) -> None:
        """Run one trading cycle"""
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Starting trading cycle at {datetime.now()}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Collect data
            signals = await self.collect_signals()
            
            # Step 2: Get market data
            market_data = await self.get_market_data()
            
            # Step 3: Generate trading opportunities
            opportunities = await self.generate_opportunities(signals, market_data)
            
            # Step 4: Make decisions
            decisions = await self.make_decisions(opportunities, market_data)
            
            # Step 5: Execute trades
            executed = await self.execute_trades(decisions)
            
            # Step 6: Update portfolio
            await self.update_portfolio()
            
            # Step 7: Monitor and report
            await self.monitor_performance()
            
            logger.info(f"✅ Trading cycle completed. Executed {len(executed)} trades")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            await self.monitor.send_alert({
                "level": "ERROR",
                "category": "SYSTEM",
                "message": f"Trading cycle failed: {str(e)}",
                "timestamp": datetime.now(),
                "details": {"error": str(e)},
                "action_required": True
            })
            
    async def collect_signals(self) -> Dict[str, List[Dict]]:
        """Collect signals from all data sources"""
        
        signals = {
            "whatsapp": [],
            "news": [],
            "technical": []
        }
        
        # Check for WhatsApp export
        whatsapp_dir = Path(__file__).parent.parent / "whatsapp_data"
        if whatsapp_dir.exists():
            latest_export = self._find_latest_export(whatsapp_dir)
            if latest_export:
                logger.info(f"Processing WhatsApp export: {latest_export}")
                messages = self.whatsapp_analyzer.parse_exported_chat(str(latest_export))
                summary = self.whatsapp_analyzer.generate_summary(messages, hours=24)
                
                # Convert to signals
                for signal in summary.get("signals", []):
                    signals["whatsapp"].append(signal)
                    
        logger.info(f"Collected signals: WhatsApp={len(signals['whatsapp'])}")
        return signals
        
    def _find_latest_export(self, directory: Path) -> Optional[Path]:
        """Find most recent WhatsApp export"""
        exports = list(directory.glob("*.txt"))
        if not exports:
            return None
        return max(exports, key=lambda p: p.stat().st_mtime)
        
    async def get_market_data(self) -> Dict[str, Any]:
        """Get current market data"""
        
        market_data = {
            "timestamp": datetime.now(),
            "conditions": {
                "vix": 16.5,  # Would fetch real VIX
                "spy_trend": "BULLISH",
                "volume": "NORMAL",
                "put_call_ratio": 0.85
            },
            "portfolio": self.portfolio_state
        }
        
        # Get prices for watched tickers
        tickers = ["AAPL", "SPY", "QQQ", "TSLA", "NVDA"]
        
        if self.mode == "simulation":
            # Use simulated prices
            for ticker in tickers:
                market_data[ticker] = {
                    "price": self.executor.get_simulated_price(ticker),
                    "volume": 1000000,
                    "change": 0.02
                }
        else:
            # Fetch real prices from Alpaca
            for ticker in tickers:
                try:
                    quote = await self.executor.get_latest_quote(ticker)
                    market_data[ticker] = {
                        "price": quote.get("price", 100),
                        "volume": quote.get("volume", 0),
                        "change": quote.get("change_percent", 0)
                    }
                except Exception as e:
                    logger.warning(f"Failed to get quote for {ticker}: {e}")
                    
        return market_data
        
    async def generate_opportunities(
        self,
        signals: Dict[str, List[Dict]],
        market_data: Dict[str, Any]
    ) -> List[Dict]:
        """Generate trading opportunities from signals"""
        
        opportunities = []
        
        # TEST MODE: Force a test trade if no signals
        if os.getenv("FORCE_TEST_TRADE") == "true" or (not any(signals.values()) and os.getenv("GITHUB_ACTIONS") == "true"):
            logger.info("TEST MODE: Generating test opportunity for SPY")
            opportunities.append({
                "ticker": "SPY",
                "action": "BUY_CALL",
                "option_type": "CALL",
                "strike": 440.0,
                "expiration": (datetime.now() + timedelta(days=7)).isoformat(),
                "confidence": 0.75,
                "strategy": "test_strategy",
                "reason": "Test trade for end-to-end validation"
            })
            return opportunities
        
        # Get top mentioned tickers from signals
        ticker_mentions = {}
        for source, source_signals in signals.items():
            for signal in source_signals:
                for ticker in signal.get("tickers", []):
                    ticker_mentions[ticker] = ticker_mentions.get(ticker, 0) + 1
                    
        # Analyze top tickers
        top_tickers = sorted(ticker_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for ticker, mentions in top_tickers:
            if ticker in market_data:
                # Use strategy engine to analyze
                strategy_signals = await self.strategy_engine.analyze_opportunity(
                    ticker=ticker,
                    current_price=market_data[ticker]["price"],
                    market_data=market_data,
                    whatsapp_signals=signals.get("whatsapp", []),
                    news_signals=signals.get("news", [])
                )
                
                for signal in strategy_signals:
                    opportunities.append({
                        "ticker": signal.ticker,
                        "action": signal.action,
                        "option_type": signal.option_type,
                        "strike": signal.strike_price,
                        "expiration": signal.expiration_date,
                        "confidence": signal.confidence,
                        "strategy": signal.strategy_name,
                        "reason": signal.reason
                    })
                    
        logger.info(f"Generated {len(opportunities)} trading opportunities")
        return opportunities
        
    async def make_decisions(
        self,
        opportunities: List[Dict],
        market_data: Dict[str, Any]
    ) -> List[Dict]:
        """Make trading decisions on opportunities"""
        
        decisions = []
        
        # If AI is enabled, use Claude for decisions
        if self.ai_enabled:
            for opp in opportunities[:3]:  # Limit to top 3
                context = TradingContext(
                    timestamp=datetime.now(),
                    ticker=opp["ticker"],
                    current_price=market_data.get(opp["ticker"], {}).get("price", 100),
                    market_conditions=market_data.get("conditions", {}),
                    whatsapp_signals=[],
                    news_sentiment={},
                    technical_indicators={},
                    recent_performance={},
                    portfolio_state=self.portfolio_state,
                    risk_metrics={"max_loss": 0.02}
                )
                
                decision = await self.decision_maker.make_decision(context)
                
                if decision.action != "HOLD":
                    decisions.append({
                        "ticker": decision.ticker,
                        "action": decision.action,
                        "option_type": decision.option_type,
                        "strike": decision.strike_price,
                        "quantity": decision.quantity,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning
                    })
        else:
            # Use rule-based decisions
            for opp in opportunities:
                if opp["confidence"] > 0.7:
                    decisions.append({
                        "ticker": opp["ticker"],
                        "action": "BUY_" + opp["option_type"],
                        "option_type": opp["option_type"],
                        "strike": opp["strike"],
                        "quantity": 1,
                        "confidence": opp["confidence"],
                        "reasoning": opp["reason"]
                    })
                    
        logger.info(f"Made {len(decisions)} trading decisions")
        return decisions
        
    async def execute_trades(self, decisions: List[Dict]) -> List[Dict]:
        """Execute trading decisions"""
        
        executed = []
        
        for decision in decisions:
            try:
                logger.info(f"Executing: {decision['action']} {decision['ticker']}")
                
                if self.mode == "simulation":
                    # Simulated execution
                    result = await self.executor.place_option_order(
                        ticker=decision["ticker"],
                        option_type=decision["option_type"],
                        strike=decision["strike"],
                        quantity=decision["quantity"],
                        side="buy"
                    )
                else:
                    # Real execution via Alpaca
                    option_symbol = f"{decision['ticker']}_{decision['option_type']}_{decision['strike']}"
                    result = await self.executor.place_option_order(
                        option_symbol=option_symbol,
                        side="buy",
                        quantity=decision["quantity"]
                    )
                    
                if result.get("success", False):
                    executed.append({
                        **decision,
                        "execution_time": datetime.now(),
                        "order_id": result.get("order_id")
                    })
                    
                    # Log to database
                    await self.db.log_trade({
                        "ticker": decision["ticker"],
                        "action": decision["action"],
                        "quantity": decision["quantity"],
                        "confidence": decision["confidence"],
                        "execution_time": datetime.now()
                    })
                    
            except Exception as e:
                logger.error(f"Failed to execute trade: {e}")
                
        return executed
        
    async def update_portfolio(self) -> None:
        """Update portfolio state"""
        
        if self.mode == "simulation":
            # Get simulated portfolio
            self.portfolio_state = {
                "total_value": self.executor.get_portfolio_value(),
                "cash": self.executor.cash,
                "positions": self.executor.get_positions(),
                "position_count": len(self.executor.positions)
            }
        else:
            # Get real portfolio from Alpaca
            try:
                account = await self.executor.get_account()
                self.portfolio_state = {
                    "total_value": float(account.get("portfolio_value", 100000)),
                    "cash": float(account.get("cash", 100000)),
                    "positions": {},  # Would fetch positions
                    "position_count": 0
                }
            except Exception as e:
                logger.error(f"Failed to update portfolio: {e}")
                
        logger.info(f"Portfolio updated: ${self.portfolio_state['total_value']:,.2f}")
        
    async def monitor_performance(self) -> None:
        """Monitor and report performance"""
        
        # Calculate metrics
        metrics = await self.monitor.calculate_metrics()
        
        # Generate report
        report = self.monitor.generate_report()
        logger.info(report)
        
        # Save metrics
        await self.monitor.save_metrics()
        
    async def run(self) -> None:
        """Main bot loop"""
        
        logger.info("🚀 Starting Trading Bot")
        
        # Initialize
        if not await self.initialize():
            logger.error("Failed to initialize bot")
            return
            
        self.running = True
        
        # Run cycles
        while self.running:
            try:
                await self.run_cycle()
                
                # Wait for next cycle (3 hours in production, 1 minute for testing)
                wait_time = 60 if self.mode == "simulation" else 3 * 3600
                logger.info(f"⏰ Waiting {wait_time} seconds until next cycle...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Stopping bot...")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
        logger.info("👋 Trading Bot stopped")


async def main():
    """Main entry point"""
    
    # Get mode from environment or default to simulation
    mode = os.getenv("TRADING_MODE", "simulation")
    
    # Create and run bot
    bot = TradingBot(mode=mode)
    await bot.run()


if __name__ == "__main__":
    # Setup logging
    logger.add(
        "logs/trading_bot_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    # Run bot
    asyncio.run(main())