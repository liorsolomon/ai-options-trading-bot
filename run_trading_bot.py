#!/usr/bin/env python3
"""
Run the trading bot with signal processing
"""

import asyncio
import os
import sys
from datetime import datetime

# Set environment
os.environ["GITHUB_ACTIONS"] = os.environ.get("GITHUB_ACTIONS", "true")

sys.path.insert(0, '.')

async def run_bot_with_signals():
    """Run the trading bot to process signals"""
    
    print("=" * 80)
    print("TRADING BOT - PROCESSING SIGNALS")
    print("=" * 80)
    
    from src.main import TradingBot
    
    # Get mode from environment
    mode = os.environ.get("TRADING_MODE", "paper")
    print(f"Trading Mode: {mode.upper()}")
    
    # Create bot
    bot = TradingBot(mode=mode)
    
    # Initialize
    print("\n1. Initializing bot...")
    if not await bot.initialize():
        print("❌ Failed to initialize bot")
        return False
    
    print(f"✅ Bot initialized")
    print(f"📊 Claude AI Status: {'ENABLED' if bot.ai_enabled else 'DISABLED'}")
    
    # Run one trading cycle to process signals
    print("\n2. Running trading cycle to process signals...")
    await bot.run_cycle()
    
    print("\n✅ Trading cycle complete")
    return True

if __name__ == "__main__":
    print(f"Starting at {datetime.now()}")
    success = asyncio.run(run_bot_with_signals())
    
    if success:
        print("\n✅ BOT RUN COMPLETE - Check logs for trades")
        sys.exit(0)
    else:
        print("\n❌ Bot run failed")
        sys.exit(1)