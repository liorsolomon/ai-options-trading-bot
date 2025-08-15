#!/usr/bin/env python3
"""
Simple test of Alpaca trading - buy and sell with proper sequencing
"""

import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest


def main():
    print("\n" + "="*60)
    print("🧪 ALPACA PAPER TRADING TEST")
    print("="*60)
    
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    trading_client = TradingClient(api_key, secret_key, paper=True)
    data_client = StockHistoricalDataClient(api_key, secret_key)
    
    # Check market status
    clock = trading_client.get_clock()
    print(f"\n📅 Market Status: {'OPEN 🟢' if clock.is_open else 'CLOSED 🔴'}")
    
    # Get account info
    account = trading_client.get_account()
    print(f"\n💰 Account Status:")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
    
    # Get SPY quote
    quote_request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
    quotes = data_client.get_stock_latest_quote(quote_request)
    spy_quote = quotes["SPY"]
    current_price = float(spy_quote.ask_price)
    
    print(f"\n📊 SPY Current Price: ${current_price:.2f}")
    
    # Check existing positions
    positions = trading_client.get_all_positions()
    spy_position = None
    
    for pos in positions:
        if pos.symbol == "SPY":
            spy_position = pos
            print(f"\n📈 Existing SPY Position Found:")
            print(f"   Quantity: {pos.qty} shares")
            print(f"   Entry Price: ${float(pos.avg_entry_price):.2f}")
            print(f"   Current Value: ${float(pos.market_value):.2f}")
            print(f"   Unrealized P&L: ${float(pos.unrealized_pl):.2f}")
            break
    
    # Check open orders
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import QueryOrderStatus
    
    request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    open_orders = trading_client.get_orders(request)
    print(f"\n📋 Open Orders: {len(open_orders)}")
    
    for order in open_orders:
        print(f"   - {order.side} {order.qty} {order.symbol} @ ", end="")
        if order.order_type == "limit":
            print(f"${float(order.limit_price):.2f} (limit)")
        else:
            print("market")
        print(f"     Order ID: {order.id}")
    
    # Test scenarios based on current state
    if open_orders:
        print("\n🧹 Cleaning up open orders...")
        for order in open_orders:
            try:
                trading_client.cancel_order_by_id(order.id)
                print(f"   ✅ Canceled: {order.id}")
            except Exception as e:
                print(f"   ❌ Could not cancel {order.id}: {e}")
    
    elif spy_position and float(spy_position.qty) > 0:
        # We have a position, let's sell it
        print("\n📉 TEST: Selling existing position...")
        
        sell_request = MarketOrderRequest(
            symbol="SPY",
            qty=1,  # Sell 1 share
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        try:
            sell_order = trading_client.submit_order(sell_request)
            print(f"   ✅ SELL Order Placed!")
            print(f"   Order ID: {sell_order.id}")
            print(f"   Status: {sell_order.status}")
            
            # Wait and check
            time.sleep(3)
            order_status = trading_client.get_order_by_id(sell_order.id)
            
            if order_status.filled_qty:
                print(f"   ✅ Order FILLED!")
                print(f"   Sold at: ${float(order_status.filled_avg_price):.2f}")
            else:
                print(f"   ⏳ Order Status: {order_status.status}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    else:
        # No position, let's buy
        print("\n📈 TEST: Placing a BUY order...")
        
        if clock.is_open:
            # Market is open - use market order
            buy_request = MarketOrderRequest(
                symbol="SPY",
                qty=1,  # Buy 1 share
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            print("   Type: Market Order (immediate execution)")
        else:
            # Market is closed - use limit order
            limit_price = round(current_price - 5, 2)  # $5 below current
            buy_request = LimitOrderRequest(
                symbol="SPY",
                qty=1,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,  # Good till canceled
                limit_price=limit_price
            )
            print(f"   Type: Limit Order at ${limit_price:.2f}")
            print("   (Will execute when market opens if price is met)")
        
        try:
            buy_order = trading_client.submit_order(buy_request)
            print(f"   ✅ BUY Order Placed!")
            print(f"   Order ID: {buy_order.id}")
            print(f"   Status: {buy_order.status}")
            
            if clock.is_open:
                # Wait for fill if market is open
                time.sleep(3)
                order_status = trading_client.get_order_by_id(buy_order.id)
                
                if order_status.filled_qty:
                    print(f"   ✅ Order FILLED!")
                    print(f"   Bought at: ${float(order_status.filled_avg_price):.2f}")
                else:
                    print(f"   ⏳ Order Status: {order_status.status}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show recent orders
    print("\n📜 Recent Order History:")
    all_request = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=5)
    recent_orders = trading_client.get_orders(all_request)
    
    for i, order in enumerate(recent_orders[:5], 1):
        print(f"\n   {i}. {order.symbol} - {order.side} {order.qty} shares")
        print(f"      Type: {order.order_type}")
        print(f"      Status: {order.status}")
        if order.filled_avg_price:
            print(f"      Filled at: ${float(order.filled_avg_price):.2f}")
        print(f"      Time: {order.submitted_at}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE!")
    print("="*60)
    print("\n📊 View your trades at: https://app.alpaca.markets")
    print("\n💡 Run this script again to execute the opposite action:")
    print("   - If you bought, next run will sell")
    print("   - If you sold, next run will buy")


if __name__ == "__main__":
    main()