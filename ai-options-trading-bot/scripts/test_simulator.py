#!/usr/bin/env python3
"""
Test the fully simulated trading environment
No market hours restrictions, instant execution
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from src.simulation.simulator import TradingSimulator
from src.database.connection import DatabaseManager
from dotenv import load_dotenv

load_dotenv()


async def test_stock_trading():
    """Test simulated stock trading"""
    
    print("\n" + "="*60)
    print("🎮 SIMULATED STOCK TRADING TEST")
    print("="*60)
    print("✅ Works anytime - no market hours!")
    print("✅ Instant execution")
    print("✅ No real money involved")
    
    # Create simulator
    sim = TradingSimulator(initial_cash=100000)
    
    print(f"\n💰 Initial Account:")
    summary = sim.get_summary()
    print(f"   Cash: ${summary['cash']:,.2f}")
    print(f"   Total Value: ${summary['total_value']:,.2f}")
    
    # Test 1: Buy SPY
    print("\n📈 Test 1: BUY 10 shares of SPY")
    spy_price = sim.get_market_price("SPY")
    print(f"   Current SPY Price: ${spy_price:.2f}")
    
    buy_order = await sim.place_order(
        symbol="SPY",
        quantity=10,
        side="BUY",
        order_type="MARKET"
    )
    
    print(f"   Order Status: {buy_order.status}")
    print(f"   Filled at: ${buy_order.filled_price:.2f}")
    print(f"   Total Cost: ${buy_order.filled_price * buy_order.quantity:.2f}")
    
    # Check positions
    print("\n📊 Current Positions:")
    for key, pos in sim.positions.items():
        print(f"   {pos.symbol}: {pos.quantity} shares @ ${pos.entry_price:.2f}")
        print(f"   Current Value: ${pos.market_value:.2f}")
    
    # Simulate price movement
    print("\n⏰ Simulating price movement...")
    for _ in range(5):
        sim.update_prices()
    
    # Check P&L
    print("\n💹 After Price Movement:")
    for key, pos in sim.positions.items():
        print(f"   {pos.symbol} Current Price: ${pos.current_price:.2f}")
        print(f"   Unrealized P&L: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_percent:.2f}%)")
    
    # Test 2: Buy more
    print("\n📈 Test 2: BUY 5 more shares of SPY")
    buy_order2 = await sim.place_order(
        symbol="SPY",
        quantity=5,
        side="BUY",
        order_type="MARKET"
    )
    print(f"   Filled at: ${buy_order2.filled_price:.2f}")
    
    # Check updated position
    print("\n📊 Updated Position:")
    spy_pos = sim.positions.get("SPY")
    if spy_pos:
        print(f"   Total Shares: {spy_pos.quantity}")
        print(f"   Average Price: ${spy_pos.entry_price:.2f}")
        print(f"   Current Value: ${spy_pos.market_value:.2f}")
    
    # Test 3: Sell some
    print("\n📉 Test 3: SELL 8 shares of SPY")
    sell_order = await sim.place_order(
        symbol="SPY",
        quantity=8,
        side="SELL",
        order_type="MARKET"
    )
    print(f"   Sold at: ${sell_order.filled_price:.2f}")
    print(f"   Proceeds: ${sell_order.filled_price * sell_order.quantity:.2f}")
    
    # Test 4: Limit order
    print("\n📝 Test 4: Place LIMIT order")
    current_price = sim.get_market_price("AAPL")
    limit_price = current_price - 5  # $5 below market
    
    print(f"   AAPL Current: ${current_price:.2f}")
    print(f"   Placing limit buy at: ${limit_price:.2f}")
    
    limit_order = await sim.place_order(
        symbol="AAPL",
        quantity=5,
        side="BUY",
        order_type="LIMIT",
        limit_price=limit_price
    )
    print(f"   Order Status: {limit_order.status}")
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL ACCOUNT SUMMARY")
    print("="*60)
    
    summary = sim.get_summary()
    print(f"   Cash: ${summary['cash']:,.2f}")
    print(f"   Positions Value: ${summary['positions_value']:,.2f}")
    print(f"   Total Value: ${summary['total_value']:,.2f}")
    print(f"   Total P&L: ${summary['total_pnl']:,.2f} ({summary['total_pnl_percent']:.2f}%)")
    print(f"   Total Orders: {summary['num_orders']}")
    
    print("\n✅ Stock trading simulation complete!")


async def test_options_trading():
    """Test simulated options trading"""
    
    print("\n" + "="*60)
    print("🎯 SIMULATED OPTIONS TRADING TEST")
    print("="*60)
    
    sim = TradingSimulator(initial_cash=100000)
    
    # Test buying a call option
    print("\n📈 Test 1: BUY CALL Option")
    spy_price = sim.get_market_price("SPY")
    strike = round(spy_price + 5)  # $5 OTM
    expiration = datetime.now() + timedelta(days=30)
    
    print(f"   SPY Current Price: ${spy_price:.2f}")
    print(f"   Buying CALL with Strike: ${strike}")
    print(f"   Expiration: {expiration.strftime('%Y-%m-%d')}")
    
    # Calculate option price
    option_price = sim.get_option_price("SPY", strike, "CALL", 30)
    print(f"   Option Price: ${option_price:.2f}")
    
    call_order = await sim.place_order(
        symbol="SPY",
        quantity=10,  # 10 contracts
        side="BUY",
        order_type="MARKET",
        is_option=True,
        strike=strike,
        expiration=expiration,
        option_type="CALL"
    )
    
    print(f"   Order Status: {call_order.status}")
    print(f"   Filled at: ${call_order.filled_price:.2f} per contract")
    print(f"   Total Cost: ${call_order.filled_price * call_order.quantity * 100:.2f}")  # x100 for options
    
    # Test buying a put option
    print("\n📉 Test 2: BUY PUT Option")
    strike = round(spy_price - 5)  # $5 OTM
    
    print(f"   Buying PUT with Strike: ${strike}")
    
    put_order = await sim.place_order(
        symbol="SPY",
        quantity=5,
        side="BUY",
        order_type="MARKET",
        is_option=True,
        strike=strike,
        expiration=expiration,
        option_type="PUT"
    )
    
    print(f"   Filled at: ${put_order.filled_price:.2f} per contract")
    print(f"   Total Cost: ${put_order.filled_price * put_order.quantity * 100:.2f}")
    
    # Simulate price movement
    print("\n⏰ Simulating market movement...")
    
    # Make SPY go up (good for calls, bad for puts)
    sim.market_prices["SPY"] *= 1.02  # 2% increase
    sim.update_prices()
    
    print(f"   SPY moved to: ${sim.get_market_price('SPY'):.2f}")
    
    # Check options P&L
    print("\n💹 Options P&L:")
    for key, pos in sim.positions.items():
        if pos.position_type == "option":
            print(f"\n   {pos.option_type} Strike ${pos.strike}:")
            print(f"   Entry: ${pos.entry_price:.2f}")
            print(f"   Current: ${pos.current_price:.2f}")
            print(f"   P&L: ${pos.unrealized_pnl * 100:.2f} ({pos.unrealized_pnl_percent:.2f}%)")
    
    # Final summary
    print("\n📊 Final Summary:")
    summary = sim.get_summary()
    print(f"   Total P&L: ${summary['total_pnl']:,.2f}")
    print(f"   Return: {summary['total_pnl_percent']:.2f}%")
    
    print("\n✅ Options trading simulation complete!")


async def test_with_database():
    """Test simulator with database logging"""
    
    print("\n" + "="*60)
    print("💾 SIMULATED TRADING WITH DATABASE")
    print("="*60)
    
    sim = TradingSimulator(initial_cash=100000)
    db = DatabaseManager()
    
    try:
        # Place a trade
        spy_price = sim.get_market_price("SPY")
        print(f"\n📈 Buying SPY at ${spy_price:.2f}")
        
        order = await sim.place_order(
            symbol="SPY",
            quantity=10,
            side="BUY",
            order_type="MARKET"
        )
        
        # Log to database
        signal_data = {
            "symbol": "SPY",
            "signal_type": "CALL",
            "confidence": 0.75,
            "underlying_price": float(spy_price),
            "strategy_name": "simulation_test",
            "claude_recommendation": "Test trade from simulator",
            "claude_confidence": 0.80,
            "trade_executed": True
        }
        
        signal_id = await db.log_signal(signal_data)
        print(f"   ✅ Signal logged to database (ID: {signal_id})")
        
        # Log the trade
        trade_data = {
            "alpaca_order_id": order.id,
            "symbol": order.symbol,
            "order_type": order.order_type,
            "side": order.side,
            "quantity": order.quantity,
            "filled_price": order.filled_price,
            "status": order.status,
            "submitted_at": order.created_at,
            "filled_at": order.filled_at
        }
        
        trade_id = await db.log_trades([trade_data])
        print(f"   ✅ Trade logged to database (ID: {trade_id[0]})")
        
        # Simulate some price movement and sell
        print("\n⏰ Simulating price movement...")
        sim.market_prices["SPY"] *= 1.01  # 1% gain
        sim.update_prices()
        
        print(f"   SPY moved to ${sim.get_market_price('SPY'):.2f}")
        
        # Sell
        print("\n📉 Selling position...")
        sell_order = await sim.place_order(
            symbol="SPY",
            quantity=10,
            side="SELL",
            order_type="MARKET"
        )
        
        print(f"   Sold at ${sell_order.filled_price:.2f}")
        
        # Calculate P&L
        pnl = (sell_order.filled_price - order.filled_price) * 10
        print(f"   P&L: ${pnl:.2f}")
        
        # Update signal with outcome
        await db.update_trade_status(
            trade_id[0],
            "CLOSED",
            exit_price=sell_order.filled_price,
            realized_pnl=pnl
        )
        
        print("\n✅ Complete trade cycle logged to database!")
        
    finally:
        await db.close()


async def main():
    """Run all simulation tests"""
    
    print("\n🎮 FULLY SIMULATED TRADING ENVIRONMENT")
    print("="*60)
    print("✅ No market hours restrictions")
    print("✅ Instant execution")
    print("✅ Test anytime, anywhere")
    print("✅ No API limits")
    
    # Test stocks
    await test_stock_trading()
    
    # Test options
    await test_options_trading()
    
    # Test with database
    await test_with_database()
    
    print("\n" + "="*60)
    print("🎉 ALL SIMULATION TESTS COMPLETE!")
    print("="*60)
    print("\nThe simulator provides:")
    print("• Instant order execution")
    print("• Realistic price movements")
    print("• Options pricing")
    print("• P&L tracking")
    print("• Database integration")
    print("\nPerfect for testing strategies without waiting for market hours!")


if __name__ == "__main__":
    asyncio.run(main())