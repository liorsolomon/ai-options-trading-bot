#!/usr/bin/env python3
"""
Force a nuclear stock trade for testing
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Set paper mode
os.environ["TRADING_MODE"] = "paper"

sys.path.insert(0, '.')

async def execute_nuclear_trade():
    """Execute a nuclear stock trade"""
    
    print("=" * 80)
    print("EXECUTING NUCLEAR STOCK TRADE - CCJ")
    print("=" * 80)
    
    from src.execution.alpaca_client import AlpacaOptionsClient
    
    # Create Alpaca client
    client = AlpacaOptionsClient()
    
    # Connect
    print("\n1. Connecting to Alpaca Paper Trading...")
    connected = await client.connect()
    
    if not connected:
        print("❌ Failed to connect to Alpaca")
        return False
    
    print("✅ Connected to Alpaca Paper Trading")
    
    # Get account info
    account = await client.get_account_info()
    print(f"\n2. Account Information:")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    
    # Try to buy CCJ stock directly (not options for now)
    print("\n3. Placing CCJ stock order...")
    print("   Symbol: CCJ (Cameco Corp)")
    print("   Quantity: 10 shares")
    print("   Order Type: Market")
    
    try:
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        # Place market order for CCJ stock
        request = MarketOrderRequest(
            symbol="CCJ",
            qty=10,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.trading_client.submit_order(request)
        
        print(f"\n✅ NUCLEAR STOCK ORDER PLACED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📋 Order ID: {order.id}")
        print(f"📊 Symbol: {order.symbol}")
        print(f"💼 Side: {order.side}")
        print(f"📦 Quantity: {order.qty} shares")
        print(f"⏰ Submitted: {order.submitted_at}")
        print(f"✅ Status: {order.status}")
        print("=" * 80)
        
        # Also try NLR ETF
        print("\n4. Placing NLR ETF order...")
        print("   Symbol: NLR (Nuclear Energy ETF)")
        print("   Quantity: 5 shares")
        
        request2 = MarketOrderRequest(
            symbol="NLR",
            qty=5,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order2 = client.trading_client.submit_order(request2)
        
        print(f"\n✅ NUCLEAR ETF ORDER PLACED!")
        print(f"📋 Order ID: {order2.id}")
        print(f"📊 Symbol: {order2.symbol}")
        print(f"📦 Quantity: {order2.qty} shares")
        
        # Check orders
        print("\n5. Checking all orders...")
        orders = await client.get_orders(status="all")
        
        print(f"\n📊 TOTAL ORDERS IN ACCOUNT: {len(orders)}")
        for ord in orders[-5:]:  # Show last 5 orders
            print(f"   - {ord['symbol']}: {ord['quantity']} @ {ord['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to place order: {e}")
        return False

if __name__ == "__main__":
    print(f"Starting at {datetime.now()}")
    success = asyncio.run(execute_nuclear_trade())
    
    if success:
        print("\n✅ NUCLEAR TRADES EXECUTED - Check your Alpaca dashboard!")
        print("You should see CCJ and NLR orders in your account")
        sys.exit(0)
    else:
        print("\n❌ Nuclear trade execution failed")
        sys.exit(1)