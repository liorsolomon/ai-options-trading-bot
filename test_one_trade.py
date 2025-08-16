#!/usr/bin/env python3
"""
Test script to execute ONE trade and show the transaction
"""

import asyncio
import os
import sys
from datetime import datetime

# Force test mode
# Use environment variable if set, otherwise default to simulation
if "TRADING_MODE" not in os.environ:
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
    
    # Get mode from environment
    mode = os.environ.get("TRADING_MODE", "simulation")
    print(f"Trading Mode: {mode.upper()}")
    
    # Create bot
    bot = TradingBot(mode=mode)
    
    # Initialize
    print("\n1. Initializing bot...")
    if not await bot.initialize():
        print("❌ Failed to initialize bot")
        return False
    
    # Check Claude AI
    print(f"✅ Bot initialized")
    print(f"📊 Claude AI Status: {'ENABLED' if bot.ai_enabled else 'DISABLED'}")
    
    # Generate test opportunity with realistic strike
    print("\n2. Generating test trade opportunity...")
    
    # Use more realistic strike near current SPY price (~550-560 range)
    # And use monthly expiration (3rd Friday)
    from datetime import timedelta
    next_friday = datetime.now()
    days_ahead = 4 - next_friday.weekday()  # Friday is weekday 4
    if days_ahead <= 0:  # Target already happened this week
        days_ahead += 7
    next_friday = next_friday + timedelta(days=days_ahead + 14)  # 2-3 weeks out
    
    opportunities = [{
        "ticker": "SPY",
        "action": "BUY_CALL",
        "option_type": "CALL",
        "strike": 560.0,  # More realistic strike for current SPY levels
        "expiration": (next_friday - datetime.now()).days,
        "confidence": 0.85,
        "strategy": "test_strategy",
        "reason": "Demonstration trade for transaction proof"
    }]
    print(f"✅ Generated opportunity: BUY CALL SPY @ $560 strike, exp in {opportunities[0]['expiration']} days")
    
    # Make decision (force it if AI says HOLD)
    print("\n3. Making trading decision...")
    market_data = {"SPY": {"price": 450.0}}
    decisions = await bot.make_decisions(opportunities, market_data)
    
    # If no decision or HOLD, force a trade
    if not decisions or len(decisions) == 0:
        print("⚠️  AI made HOLD decision - forcing trade for demonstration")
        decisions = [{
            "ticker": "SPY",
            "action": "BUY_CALL",
            "option_type": "CALL",
            "strike": 560.0,  # Match the opportunity strike
            "quantity": 1,
            "expiration": opportunities[0]["expiration"],
            "confidence": 0.75,
            "reasoning": "Forced trade for transaction demonstration"
        }]
    
    print(f"✅ Decision: {decisions[0]['action']} {decisions[0]['quantity']} contracts")
    
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