#!/usr/bin/env python3
"""
Test a single trading cycle locally
"""

import asyncio
import os
import sys

# Set up environment
os.environ["TRADING_MODE"] = "simulation"
os.environ["GITHUB_ACTIONS"] = "true"  # Force test mode

# Add src to path
sys.path.insert(0, '.')

from src.main import TradingBot

async def run_single_cycle():
    """Run a single trading cycle"""
    print("=" * 60)
    print("TESTING SINGLE TRADING CYCLE")
    print("=" * 60)
    
    # Create bot
    bot = TradingBot(mode='simulation')
    
    # Initialize
    print("\n1. Initializing bot...")
    if not await bot.initialize():
        print("❌ Failed to initialize bot")
        return False
    
    print("✅ Bot initialized successfully")
    
    # Check Claude AI status
    if bot.ai_enabled:
        print("✅ Claude AI is ENABLED")
    else:
        print("⚠️  Claude AI is DISABLED")
    
    # Run one cycle
    print("\n2. Running trading cycle...")
    await bot.run_cycle()
    
    print("\n" + "=" * 60)
    print("✅ TRADING CYCLE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(run_single_cycle())
    sys.exit(0 if success else 1)