#!/usr/bin/env python3
"""
Test trading locally without deployment
"""

import os
import sys
import asyncio
from pathlib import Path

# Set up environment
os.environ['ALPACA_API_KEY'] = 'PKQ098Y6FYCOHG0GKUDT'
os.environ['ALPACA_SECRET_KEY'] = 'tB1cgKUDvTOur2x51grsWgmXHc2wocKyY3l1J9V2'
os.environ['TRADING_MODE'] = 'paper'
os.environ['FORCE_TEST_TRADE'] = 'true'
os.environ['DATABASE_URL'] = 'postgresql://postgres.lqqcnbwqvfxlympbmymv:hhD0IlcEjabcsq9V@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import TradingBot

async def test_trade():
    """Run a test trade cycle"""
    print("🚀 Starting local test trade...")
    
    try:
        bot = TradingBot()
        print("✅ Bot initialized")
        
        if await bot.initialize():
            print("✅ Components initialized")
            
            # Run one cycle
            await bot.run_cycle()
            print("✅ Trade cycle completed")
        else:
            print("❌ Failed to initialize bot")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_trade())