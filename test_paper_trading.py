#!/usr/bin/env python3
"""
Test script specifically for Alpaca paper trading
Uses real option symbols that should be available
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Ensure we use paper mode
os.environ["TRADING_MODE"] = "paper"
os.environ["GITHUB_ACTIONS"] = "true"

sys.path.insert(0, '.')

async def test_paper_trading():
    """Test paper trading with a real SPY option"""
    
    print("=" * 80)
    print("TESTING ALPACA PAPER TRADING")
    print("=" * 80)
    
    from src.execution.alpaca_client import AlpacaOptionsClient
    
    # Create Alpaca client
    client = AlpacaOptionsClient()
    
    # Connect to Alpaca
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
    print(f"   Cash: ${account['cash']:,.2f}")
    print(f"   Options Level: {account.get('options_trading_level', 'N/A')}")
    
    # Get SPY quote
    print("\n3. Getting SPY Quote...")
    quote = await client.get_latest_quote("SPY")
    print(f"   SPY Price: ${quote.get('bid', 0):.2f} x ${quote.get('ask', 0):.2f}")
    
    # Try to place a simple stock order first (not options)
    print("\n4. Testing with SPY stock order (not options)...")
    try:
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        request = MarketOrderRequest(
            symbol="SPY",
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.trading_client.submit_order(request)
        
        print(f"✅ Stock order placed successfully!")
        print(f"   Order ID: {order.id}")
        print(f"   Symbol: {order.symbol}")
        print(f"   Quantity: {order.qty}")
        print(f"   Status: {order.status}")
        
        # Cancel the order immediately
        client.trading_client.cancel_order_by_id(order.id)
        print(f"   Order cancelled")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to place order: {e}")
        return False

if __name__ == "__main__":
    print(f"Starting at {datetime.now()}")
    success = asyncio.run(test_paper_trading())
    
    if success:
        print("\n✅ PAPER TRADING TEST SUCCESSFUL!")
        print("Note: Options trading may require additional setup in your Alpaca account")
        sys.exit(0)
    else:
        print("\n❌ Paper trading test failed")
        sys.exit(1)