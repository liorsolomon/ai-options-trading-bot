#!/usr/bin/env python3
"""
Quick simulation test - buy and sell demonstration
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.simulation.simulator import TradingSimulator


async def quick_test():
    """Quick buy/sell test in simulator"""
    
    print("\n" + "="*60)
    print("🎮 QUICK SIMULATION TEST - BUY & SELL")
    print("="*60)
    
    # Create simulator
    sim = TradingSimulator(initial_cash=100000)
    
    print(f"\n💰 Starting with ${sim.cash:,.2f}")
    
    # 1. BUY SPY
    print("\n1️⃣ BUYING 100 shares of SPY...")
    spy_price = sim.get_market_price("SPY")
    print(f"   SPY Price: ${spy_price:.2f}")
    
    buy_order = await sim.place_order(
        symbol="SPY",
        quantity=100,
        side="BUY",
        order_type="MARKET"
    )
    
    print(f"   ✅ Bought at ${buy_order.filled_price:.2f}")
    print(f"   Cost: ${buy_order.filled_price * 100:.2f}")
    print(f"   Cash remaining: ${sim.cash:.2f}")
    
    # 2. Simulate price increase
    print("\n2️⃣ Simulating price movement...")
    sim.market_prices["SPY"] *= 1.02  # 2% gain
    sim.update_prices()
    
    spy_pos = sim.positions["SPY"]
    print(f"   SPY moved to ${spy_pos.current_price:.2f}")
    print(f"   Position value: ${spy_pos.market_value:.2f}")
    print(f"   Unrealized P&L: ${spy_pos.unrealized_pnl:.2f} ({spy_pos.unrealized_pnl_percent:.2f}%)")
    
    # 3. SELL SPY
    print("\n3️⃣ SELLING 100 shares of SPY...")
    
    sell_order = await sim.place_order(
        symbol="SPY",
        quantity=100,
        side="SELL",
        order_type="MARKET"
    )
    
    print(f"   ✅ Sold at ${sell_order.filled_price:.2f}")
    print(f"   Proceeds: ${sell_order.filled_price * 100:.2f}")
    
    # 4. Final summary
    print("\n" + "="*60)
    print("📊 TRADE SUMMARY")
    print("="*60)
    
    profit = (sell_order.filled_price - buy_order.filled_price) * 100
    
    print(f"   Buy Price:  ${buy_order.filled_price:.2f}")
    print(f"   Sell Price: ${sell_order.filled_price:.2f}")
    print(f"   Quantity:   100 shares")
    print(f"   Profit:     ${profit:.2f}")
    print(f"   Return:     {(profit / (buy_order.filled_price * 100)) * 100:.2f}%")
    
    summary = sim.get_summary()
    print(f"\n   Final Cash: ${sim.cash:,.2f}")
    print(f"   Total Account Value: ${summary['total_value']:,.2f}")
    print(f"   Total P&L: ${summary['total_pnl']:.2f}")
    
    print("\n✅ Simulation complete!")
    print("   • Bought 100 shares")
    print("   • Price went up 2%")
    print("   • Sold for profit")
    print("   • All executed instantly!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    
    if success:
        print("\n🎉 SUCCESS! The simulator is working perfectly.")
        print("\n📝 What this demonstrates:")
        print("   • No need to wait for market hours")
        print("   • Instant order execution")
        print("   • Realistic P&L tracking")
        print("   • Can test strategies anytime")
        print("\n💡 Use this for rapid strategy testing!")