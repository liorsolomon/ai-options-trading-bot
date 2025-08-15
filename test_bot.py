#!/usr/bin/env python3
"""
Quick test script for the trading bot
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

async def test_bot():
    """Test bot initialization and one cycle"""
    from main import TradingBot
    
    print("\n" + "="*60)
    print("🧪 TESTING TRADING BOT")
    print("="*60)
    
    # Create bot in simulation mode
    bot = TradingBot(mode="simulation")
    
    # Initialize
    print("\n📦 Initializing components...")
    success = await bot.initialize()
    
    if not success:
        print("❌ Failed to initialize")
        return
        
    print("✅ Initialized successfully!")
    
    # Run one cycle
    print("\n🔄 Running one trading cycle...")
    await bot.run_cycle()
    
    print("\n✅ Test completed successfully!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_bot())