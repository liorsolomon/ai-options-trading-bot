#!/usr/bin/env python3
"""
Test script to execute ONE trade and show the transaction
"""

import asyncio
import os
import sys
from datetime import datetime

# Force test mode
os.environ["TRADING_MODE"] = "simulation"
os.environ["GITHUB_ACTIONS"] = "true"
os.environ["FORCE_TEST_TRADE"] = "true"

sys.path.insert(0, '.')

async def execute_one_trade():
    """Execute a single trade and show the transaction"""
    
    print("=" * 80)
    print("EXECUTING ONE TRADE - TRANSACTION PROOF")
    print("=" * 80)
    
    from src.main import TradingBot
    
    # Create bot
    bot = TradingBot(mode='simulation')
    
    # Initialize
    print("\n1. Initializing bot...")
    if not await bot.initialize():
        print("❌ Failed to initialize bot")
        return False
    
    # Check Claude AI
    print(f"✅ Bot initialized")
    print(f"📊 Claude AI Status: {'ENABLED' if bot.ai_enabled else 'DISABLED'}")
    
    # Generate test opportunity
    print("\n2. Generating test trade opportunity...")
    opportunities = [{
        "ticker": "SPY",
        "action": "BUY_CALL",
        "option_type": "CALL",
        "strike": 440.0,
        "expiration": 7,
        "confidence": 0.85,
        "strategy": "test_strategy",
        "reason": "Demonstration trade for transaction proof"
    }]
    print(f"✅ Generated opportunity: BUY CALL SPY @ $440 strike")
    
    # Make decision
    print("\n3. Making trading decision...")
    market_data = {"SPY": {"price": 450.0}}
    decisions = await bot.make_decisions(opportunities, market_data)
    if decisions:
        print(f"✅ Decision made: {decisions[0]['action']} {decisions[0]['quantity']} contracts")
    else:
        print("❌ No decision made")
        return False
    
    # Execute trade
    print("\n4. EXECUTING TRADE...")
    print("-" * 40)
    
    executed = await bot.execute_trades(decisions)
    
    if executed:
        trade = executed[0]
        print("\n" + "=" * 80)
        print("🎯 TRANSACTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📋 Order ID: {trade['order_id']}")
        print(f"📊 Symbol: {trade['ticker']}")
        print(f"💼 Action: {trade['action']}")
        print(f"📈 Type: {trade['option_type']}")
        print(f"💰 Strike: ${trade['strike']}")
        print(f"📦 Quantity: {trade['quantity']} contracts")
        print(f"⏰ Execution Time: {trade['execution_time']}")
        print(f"✅ Status: {trade['status']}")
        print("=" * 80)
        
        # Show portfolio
        await bot.update_portfolio()
        print(f"\n💼 PORTFOLIO AFTER TRADE:")
        print(f"   Cash: ${bot.portfolio_state['cash']:,.2f}")
        print(f"   Positions: {bot.portfolio_state['position_count']}")
        print(f"   Total Value: ${bot.portfolio_state['total_value']:,.2f}")
        print("=" * 80)
        
        return True
    else:
        print("❌ Trade execution failed - no transactions")
        return False

if __name__ == "__main__":
    print(f"Starting at {datetime.now()}")
    success = asyncio.run(execute_one_trade())
    
    if success:
        print("\n✅ TRANSACTION PROOF COMPLETE - Trade executed successfully!")
        sys.exit(0)
    else:
        print("\n❌ No transaction executed")
        sys.exit(1)