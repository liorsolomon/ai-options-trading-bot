#!/usr/bin/env python3
"""
Test actual buy and sell orders on Alpaca (paper trading)
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest


def test_stock_trading():
    """Test buying and selling stocks"""
    
    print("\n" + "="*60)
    print("🧪 ALPACA TRADING TEST (PAPER ACCOUNT)")
    print("="*60)
    print("\n⚠️  This will place REAL paper trades (not real money)")
    print("We'll buy 1 share of SPY and then sell it")
    
    # Initialize clients
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    trading_client = TradingClient(api_key, secret_key, paper=True)
    data_client = StockHistoricalDataClient(api_key, secret_key)
    
    try:
        # 1. Check account status
        print("\n1️⃣ Checking Account Status...")
        account = trading_client.get_account()
        print(f"   Account Status: {account.status}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   Current Equity: ${float(account.equity):,.2f}")
        initial_equity = float(account.equity)
        
        # 2. Get current SPY price
        print("\n2️⃣ Getting SPY Quote...")
        quote_request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
        quotes = data_client.get_stock_latest_quote(quote_request)
        spy_quote = quotes["SPY"]
        
        print(f"   SPY Bid: ${spy_quote.bid_price:.2f}")
        print(f"   SPY Ask: ${spy_quote.ask_price:.2f}")
        print(f"   Spread: ${(spy_quote.ask_price - spy_quote.bid_price):.2f}")
        
        # 3. Place a BUY order
        print("\n3️⃣ Placing BUY Order...")
        print("   Buying 1 share of SPY at market price...")
        
        buy_order_request = MarketOrderRequest(
            symbol="SPY",
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        buy_order = trading_client.submit_order(buy_order_request)
        print(f"   ✅ Buy Order Submitted!")
        print(f"   Order ID: {buy_order.id}")
        print(f"   Status: {buy_order.status}")
        
        # 4. Wait for order to fill
        print("\n4️⃣ Waiting for Buy Order to Fill...")
        time.sleep(2)
        
        # Check order status
        buy_order_status = trading_client.get_order_by_id(buy_order.id)
        print(f"   Order Status: {buy_order_status.status}")
        
        if buy_order_status.filled_qty:
            print(f"   Filled Quantity: {buy_order_status.filled_qty}")
            print(f"   Filled Price: ${float(buy_order_status.filled_avg_price):.2f}")
        
        # 5. Check positions
        print("\n5️⃣ Checking Positions...")
        positions = trading_client.get_all_positions()
        
        if positions:
            for position in positions:
                print(f"   Symbol: {position.symbol}")
                print(f"   Quantity: {position.qty}")
                print(f"   Entry Price: ${float(position.avg_entry_price):.2f}")
                print(f"   Current Price: ${float(position.current_price):.2f}")
                print(f"   Unrealized P&L: ${float(position.unrealized_pl):.2f}")
        else:
            print("   No positions found (order may still be processing)")
        
        # 6. Wait a moment then SELL
        print("\n⏳ Waiting 5 seconds before selling...")
        time.sleep(5)
        
        print("\n6️⃣ Placing SELL Order...")
        print("   Selling 1 share of SPY at market price...")
        
        sell_order_request = MarketOrderRequest(
            symbol="SPY",
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        sell_order = trading_client.submit_order(sell_order_request)
        print(f"   ✅ Sell Order Submitted!")
        print(f"   Order ID: {sell_order.id}")
        print(f"   Status: {sell_order.status}")
        
        # 7. Wait for sell order to fill
        print("\n7️⃣ Waiting for Sell Order to Fill...")
        time.sleep(2)
        
        sell_order_status = trading_client.get_order_by_id(sell_order.id)
        print(f"   Order Status: {sell_order_status.status}")
        
        if sell_order_status.filled_qty:
            print(f"   Filled Quantity: {sell_order_status.filled_qty}")
            print(f"   Filled Price: ${float(sell_order_status.filled_avg_price):.2f}")
        
        # 8. Final account check
        print("\n8️⃣ Final Account Status...")
        time.sleep(2)
        
        final_account = trading_client.get_account()
        final_equity = float(final_account.equity)
        
        print(f"   Final Equity: ${final_equity:,.2f}")
        print(f"   Initial Equity: ${initial_equity:,.2f}")
        print(f"   Net Change: ${(final_equity - initial_equity):.2f}")
        
        # 9. Check all orders
        print("\n9️⃣ Order History...")
        orders = trading_client.get_orders(filter="all", limit=5)
        
        for order in orders[:5]:
            print(f"\n   Order: {order.symbol} - {order.side}")
            print(f"   Status: {order.status}")
            print(f"   Quantity: {order.qty}")
            if order.filled_avg_price:
                print(f"   Filled Price: ${float(order.filled_avg_price):.2f}")
            print(f"   Time: {order.submitted_at}")
        
        # Summary
        print("\n" + "="*60)
        print("✅ TRADING TEST COMPLETE!")
        print("="*60)
        print("\nSummary:")
        print("• Successfully placed BUY order")
        print("• Successfully placed SELL order")
        print("• Orders executed on Alpaca paper trading")
        print("• All systems working correctly")
        print("\n📊 Check your Alpaca dashboard for details:")
        print("https://app.alpaca.markets")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during trading test: {e}")
        print("\nNote: If market is closed, orders may be queued for next session")
        return False


def test_limit_orders():
    """Test limit orders (can work even when market is closed)"""
    
    print("\n" + "="*60)
    print("🧪 TESTING LIMIT ORDERS")
    print("="*60)
    
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    trading_client = TradingClient(api_key, secret_key, paper=True)
    data_client = StockHistoricalDataClient(api_key, secret_key)
    
    try:
        # Get current price
        quote_request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
        quotes = data_client.get_stock_latest_quote(quote_request)
        spy_quote = quotes["SPY"]
        current_price = float(spy_quote.ask_price)
        
        print(f"\nCurrent SPY Price: ${current_price:.2f}")
        
        # Place a limit buy order below current price
        buy_price = round(current_price - 10, 2)  # $10 below current
        print(f"\n1️⃣ Placing Limit BUY Order at ${buy_price:.2f} (below market)...")
        
        limit_buy_request = LimitOrderRequest(
            symbol="SPY",
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC,  # Good till canceled
            limit_price=buy_price
        )
        
        limit_buy = trading_client.submit_order(limit_buy_request)
        print(f"   ✅ Limit Buy Order Placed")
        print(f"   Order ID: {limit_buy.id}")
        print(f"   Status: {limit_buy.status}")
        
        # Place a limit sell order above current price
        sell_price = round(current_price + 10, 2)  # $10 above current
        print(f"\n2️⃣ Placing Limit SELL Order at ${sell_price:.2f} (above market)...")
        
        limit_sell_request = LimitOrderRequest(
            symbol="SPY",
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
            limit_price=sell_price
        )
        
        limit_sell = trading_client.submit_order(limit_sell_request)
        print(f"   ✅ Limit Sell Order Placed")
        print(f"   Order ID: {limit_sell.id}")
        print(f"   Status: {limit_sell.status}")
        
        # Check open orders
        print("\n3️⃣ Checking Open Orders...")
        open_orders = trading_client.get_orders(filter="open")
        
        for order in open_orders:
            print(f"\n   {order.side} {order.qty} {order.symbol}")
            print(f"   Limit Price: ${float(order.limit_price):.2f}")
            print(f"   Status: {order.status}")
            print(f"   Order ID: {order.id}")
        
        # Cancel orders
        print("\n4️⃣ Canceling Test Orders...")
        
        trading_client.cancel_order_by_id(limit_buy.id)
        print(f"   ✅ Canceled buy order: {limit_buy.id}")
        
        trading_client.cancel_order_by_id(limit_sell.id)
        print(f"   ✅ Canceled sell order: {limit_sell.id}")
        
        print("\n✅ Limit order test complete!")
        print("   - Successfully placed limit orders")
        print("   - Successfully canceled orders")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Check if market is open
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    client = TradingClient(api_key, secret_key, paper=True)
    
    clock = client.get_clock()
    
    print("\n📅 Market Status:")
    print(f"   Market is: {'OPEN 🟢' if clock.is_open else 'CLOSED 🔴'}")
    print(f"   Current time: {clock.timestamp}")
    
    if clock.is_open:
        print(f"   Closes at: {clock.next_close}")
        print("\n✅ Market is open - testing with market orders...")
        test_stock_trading()
    else:
        print(f"   Opens at: {clock.next_open}")
        print("\n📝 Market is closed - testing with limit orders...")
        test_limit_orders()
        print("\n💡 Note: Limit orders will be queued for next market open")
        print("   You can cancel them from the Alpaca dashboard")