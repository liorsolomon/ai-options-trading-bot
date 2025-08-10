#!/usr/bin/env python3
"""
Run hypothesis tests to validate trading strategies
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.simulation.hypothesis_tester import HypothesisTester


async def quick_hypothesis_test():
    """Run a quick hypothesis test"""
    
    print("\n" + "="*60)
    print("🔬 QUICK HYPOTHESIS TEST")
    print("="*60)
    print("\nTesting: 'Momentum signals generate profitable options trades'")
    print("Success criteria: Win rate > 55%, Avg return > 2%")
    
    tester = HypothesisTester(initial_capital=100000)
    
    # Run a quick test with fewer trades for demonstration
    test = await tester.test_momentum_hypothesis(num_trades=20)
    
    # Print results
    tester.print_summary(test)
    
    # Show sample trades
    print("\n📝 Sample Trades:")
    for i, trade in enumerate(test.trades[:5], 1):
        print(f"\n   Trade {i}:")
        print(f"   Signal: {trade['signal']}")
        print(f"   Entry: ${trade['entry_price']:.2f}")
        print(f"   Exit: ${trade['exit_price']:.2f}")
        print(f"   P&L: ${trade['pnl']:.2f}")
        print(f"   Return: {trade['return_pct']:.2%}")
    
    print("\n" + "="*60)
    print("💡 WHAT THIS MEANS:")
    print("="*60)
    
    if test.is_successful:
        print("\n✅ Your hypothesis shows promise!")
        print("   • The strategy met your success criteria")
        print("   • Consider testing with more trades")
        print("   • Ready for extended simulation testing")
    else:
        print("\n⚠️  Hypothesis needs refinement")
        print("   • The strategy didn't meet success criteria")
        print("   • Try adjusting parameters")
        print("   • Test different market conditions")
    
    print("\n📊 Next Steps:")
    print("1. Run more extensive tests (100+ trades)")
    print("2. Test in different market conditions")
    print("3. Compare multiple strategies")
    print("4. Refine parameters based on results")
    print("5. Move successful strategies to paper trading")
    
    return test


if __name__ == "__main__":
    test = asyncio.run(quick_hypothesis_test())
    
    print("\n🎯 Your testing framework is ready!")
    print("\nYou can now:")
    print("• Test any trading hypothesis quickly")
    print("• No market hours restrictions")
    print("• Validate strategies before live trading")
    print("• Build confidence in your approach")
    print("\nPerfect for the next few weeks of hypothesis validation!")