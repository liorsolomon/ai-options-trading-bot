#!/usr/bin/env python3
"""
Analyze WhatsApp group export for trading signals
Perfect for investChatIL group analysis
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.data_sources.whatsapp_collector import WhatsAppAnalyzer


def main():
    print("\n" + "="*60)
    print("📱 WHATSAPP GROUP ANALYZER - investChatIL")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("""
Usage: python analyze_whatsapp.py <exported_chat.txt>

How to export WhatsApp chat:
1. Open WhatsApp → investChatIL group
2. Click ⋮ (menu) → More → Export chat
3. Choose "Without media"
4. Save the .txt file
5. Run: python analyze_whatsapp.py WhatsApp_Chat.txt

The analyzer will:
✅ Extract stock tickers mentioned
✅ Analyze sentiment (bullish/bearish)
✅ Identify high-confidence signals
✅ Generate testable hypotheses
✅ Support Hebrew terms (קול/פוט)
        """)
        return
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📂 Analyzing: {file_path}")
    
    analyzer = WhatsAppAnalyzer()
    
    # Parse messages
    print("📝 Parsing messages...")
    messages = analyzer.parse_exported_chat(file_path)
    print(f"   Found {len(messages)} messages")
    
    # Generate summary
    print("\n📊 Generating summary...")
    summary = analyzer.generate_summary(messages, hours=168)  # Last week
    
    # Display results
    print("\n" + "="*60)
    print("📈 ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📊 Group Activity (Last Week):")
    print(f"   Total Messages: {summary.get('total_messages', 0)}")
    print(f"   Active Members: {summary.get('unique_senders', 0)}")
    
    print(f"\n💭 Sentiment Analysis:")
    print(f"   Bullish Signals: {summary.get('bullish_signals', 0)}")
    print(f"   Bearish Signals: {summary.get('bearish_signals', 0)}")
    sentiment = summary.get('overall_sentiment', 0)
    sentiment_text = "🟢 BULLISH" if sentiment > 0.2 else "🔴 BEARISH" if sentiment < -0.2 else "⚪ NEUTRAL"
    print(f"   Overall Sentiment: {sentiment:.2f} {sentiment_text}")
    
    if summary.get("top_tickers"):
        print(f"\n🎯 Most Discussed Stocks:")
        for ticker, count in summary["top_tickers"][:10]:
            bar = "█" * min(20, count)
            print(f"   {ticker:6} {count:3}x {bar}")
    
    if summary.get("signals"):
        print(f"\n⚡ High-Confidence Signals:")
        for signal in summary["signals"][:5]:
            print(f"\n   Time: {signal['time']}")
            print(f"   Tickers: {', '.join(signal['tickers']) if signal['tickers'] else 'General'}")
            print(f"   Signal: {signal['signal']} (confidence: {signal['confidence']:.0%})")
            print(f"   Preview: {signal['preview'][:50]}...")
    
    # Generate hypotheses
    hypotheses = analyzer.create_hypothesis(summary)
    if hypotheses:
        print(f"\n💡 Testable Hypotheses:")
        for i, hyp in enumerate(hypotheses, 1):
            print(f"   {i}. {hyp}")
    
    # Save results
    output_dir = Path("whatsapp_analysis")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    import json
    summary_file = output_dir / f"summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    # Save hypotheses
    if hypotheses:
        hyp_file = output_dir / f"hypotheses_{timestamp}.txt"
        with open(hyp_file, 'w', encoding='utf-8') as f:
            f.write("GENERATED HYPOTHESES FROM investChatIL\n")
            f.write("="*50 + "\n\n")
            for i, hyp in enumerate(hypotheses, 1):
                f.write(f"{i}. {hyp}\n")
    
    print(f"\n✅ Analysis saved to: {output_dir}/")
    
    print("\n" + "="*60)
    print("🚀 NEXT STEPS")
    print("="*60)
    print("""
1. Review the high-confidence signals above
2. Test the hypotheses in the simulator:
   python scripts/run_hypothesis_tests.py

3. For continuous monitoring:
   - Export chat weekly
   - Run this analysis
   - Track which signals work

4. Integration ideas:
   - Upload exports to GitHub
   - Automate analysis in GitHub Actions
   - Weight signals by member track record
    """)


if __name__ == "__main__":
    main()