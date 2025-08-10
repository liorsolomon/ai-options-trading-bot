#!/usr/bin/env python3
"""
Test script to verify Alpaca API connection and permissions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from datetime import datetime


def test_connection():
    """Test Alpaca API connection and permissions"""
    
    print("🔧 Testing Alpaca API Connection...")
    print("=" * 50)
    
    try:
        # Initialize trading client
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key or not secret_key:
            print("❌ ERROR: API keys not found in .env file")
            return False
        
        print(f"📍 Using API Key: {api_key[:10]}...")
        print(f"📍 Base URL: {os.getenv('ALPACA_BASE_URL')}")
        
        # Create trading client
        trading_client = TradingClient(
            api_key=api_key,
            secret_key=secret_key,
            paper=True
        )
        
        # Test 1: Get account information
        print("\n1️⃣ Testing Account Access...")
        account = trading_client.get_account()
        print(f"✅ Account Status: {account.status}")
        print(f"   - Account Number: {account.account_number}")
        print(f"   - Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   - Cash: ${float(account.cash):,.2f}")
        print(f"   - Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   - Pattern Day Trader: {account.pattern_day_trader}")
        print(f"   - Trading Blocked: {account.trading_blocked}")
        
        # Check options trading level
        options_level = getattr(account, 'options_trading_level', None)
        options_approved = getattr(account, 'options_approved_level', None)
        
        if options_level:
            print(f"   - Options Trading Level: {options_level}")
        if options_approved:
            print(f"   - Options Approved Level: {options_approved}")
        
        if not options_level and not options_approved:
            print("⚠️  WARNING: Options trading level not detected")
            print("   Please enable options trading in your Alpaca account")
        
        # Test 2: Check market data access
        print("\n2️⃣ Testing Market Data Access...")
        stock_client = StockHistoricalDataClient(api_key, secret_key)
        
        # Get a test quote
        request = StockLatestQuoteRequest(symbol_or_symbols="SPY")
        quote = stock_client.get_stock_latest_quote(request)
        
        if "SPY" in quote:
            spy_quote = quote["SPY"]
            print(f"✅ Market Data Access Working")
            print(f"   - SPY Bid: ${float(spy_quote.bid_price):.2f}")
            print(f"   - SPY Ask: ${float(spy_quote.ask_price):.2f}")
            print(f"   - Quote Time: {spy_quote.timestamp}")
        
        # Test 3: Check positions
        print("\n3️⃣ Checking Current Positions...")
        positions = trading_client.get_all_positions()
        if positions:
            print(f"📊 Found {len(positions)} open position(s):")
            for pos in positions[:5]:  # Show first 5
                print(f"   - {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
        else:
            print("✅ No open positions (clean slate)")
        
        # Test 4: Check recent orders
        print("\n4️⃣ Checking Recent Orders...")
        orders = trading_client.get_orders()
        if orders:
            print(f"📋 Found {len(orders)} order(s):")
            for order in orders[:3]:  # Show first 3
                print(f"   - {order.symbol}: {order.side} {order.qty} @ {order.order_type}")
        else:
            print("✅ No open orders")
        
        # Test 5: Check if market is open
        print("\n5️⃣ Market Status...")
        clock = trading_client.get_clock()
        if clock.is_open:
            print(f"✅ Market is OPEN")
        else:
            print(f"🔴 Market is CLOSED")
        print(f"   - Next Open: {clock.next_open}")
        print(f"   - Next Close: {clock.next_close}")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Alpaca connection is working.")
        print("\n⚠️  IMPORTANT REMINDERS:")
        print("1. This is a PAPER TRADING account (not real money)")
        print("2. You need Options Level 2 approval for options trading")
        print("3. Add these credentials to GitHub Secrets for automation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API keys")
        print("2. Network connection problems")
        print("3. Alpaca service issues")
        print("\nPlease verify your credentials and try again.")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)