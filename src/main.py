#!/usr/bin/env python3
"""
Main entry point for the AI Options Trading Bot
"""

import asyncio
import sys
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
import os

from src.claude_integration.client import ClaudeClient
from src.data_sources.market_data import MarketDataAggregator
from src.strategies.strategy_manager import StrategyManager
from src.signals.signal_generator import SignalGenerator
from src.execution.trade_executor import TradeExecutor
from src.database.connection import DatabaseManager
from src.utils.config_loader import load_config

load_dotenv()

logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))
logger.add("logs/trading_bot_{time}.log", rotation="1 day", retention="30 days")


class TradingBot:
    def __init__(self):
        logger.info("Initializing Trading Bot...")
        
        self.config = load_config()
        self.db_manager = DatabaseManager()
        self.claude_client = ClaudeClient()
        self.market_data = MarketDataAggregator()
        self.strategy_manager = StrategyManager(self.config)
        self.signal_generator = SignalGenerator()
        self.trade_executor = TradeExecutor()
        
        logger.info("Trading Bot initialized successfully")
    
    async def run_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            logger.info(f"Starting trading cycle at {datetime.now()}")
            
            # Step 1: Collect market data
            logger.info("Collecting market data...")
            market_snapshot = await self.market_data.collect_all_data()
            
            # Step 2: Generate signals from various strategies
            logger.info("Generating trading signals...")
            raw_signals = await self.strategy_manager.analyze_market(market_snapshot)
            
            # Step 3: Get Claude's analysis
            logger.info("Getting AI analysis from Claude...")
            claude_analysis = await self.claude_client.analyze_market(
                market_snapshot, 
                raw_signals
            )
            
            # Step 4: Combine signals and make final decision
            logger.info("Combining signals for final decision...")
            final_signals = await self.signal_generator.combine_signals(
                raw_signals,
                claude_analysis,
                market_snapshot
            )
            
            # Step 5: Execute trades if signals meet criteria
            if final_signals:
                logger.info(f"Executing {len(final_signals)} trades...")
                execution_results = await self.trade_executor.execute_signals(
                    final_signals
                )
                
                # Step 6: Log results to database
                await self.db_manager.log_trades(execution_results)
                
                logger.info(f"Trading cycle completed. Executed {len(execution_results)} trades")
            else:
                logger.info("No tradeable signals generated in this cycle")
            
            # Step 7: Monitor existing positions
            await self.trade_executor.monitor_positions()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            await self.db_manager.log_error(str(e))
            raise
    
    async def shutdown(self):
        """Clean shutdown of all connections"""
        logger.info("Shutting down Trading Bot...")
        await self.db_manager.close()
        await self.market_data.close()
        await self.trade_executor.close()
        logger.info("Trading Bot shutdown complete")


async def main():
    """Main entry point"""
    bot = TradingBot()
    
    try:
        await bot.run_trading_cycle()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())