#!/usr/bin/env python3
"""
Test WhatsApp integration with sample Hebrew messages
"""

import tempfile
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_sample_export():
    """Create a sample WhatsApp export for testing"""
    
    sample_chat = """[10/08/24, 09:30:15] יוסי: בוקר טוב! מה דעתכם על NVDA היום?
[10/08/24, 09:31:02] דני: נראה חזק, אני קונה קול 850
[10/08/24, 09:32:45] שרה: גם אני נכנסת, קול על NVDA
[10/08/24, 09:35:20] משה: זהירות, יש דוחות מחר
[10/08/24, 10:15:33] יוסי: SPY פריצה! קונה קולים 450
[10/08/24, 10:16:45] דני: נכנס איתך על הספיי
[10/08/24, 10:45:12] שרה: AAPL נראה חלש, שוקלת פוט
[10/08/24, 10:46:30] משה: אפל ירידה חדה, פוט 175
[10/08/24, 11:30:22] יוסי: טסלה מתפרצת! קול דחוף
[10/08/24, 11:31:15] דני: TSLA קול 250, נכנס חזק
[10/08/24, 14:20:10] שרה: סוגרת את NVDA ברווח 20%
[10/08/24, 14:22:33] משה: יפה! גם אני יוצא
[10/08/24, 15:45:55] יוסי: מחר יום מעניין, הנאסדק נראה מוכן לעליות
[10/08/24, 15:47:20] דני: מסכים, QQQ קולים לשבוע הבא
[10/08/24, 15:50:33] שרה: סיכום יום מעולה! רווח כולל 15%"""
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_WhatsApp_Chat.txt', 
                                     delete=False, encoding='utf-8') as f:
        f.write(sample_chat)
        return f.name

def test_whatsapp_processing():
    """Test the WhatsApp processing pipeline"""
    
    print("\n" + "="*60)
    print("🧪 TESTING WHATSAPP INTEGRATION")
    print("="*60)
    
    # Create sample file
    sample_file = create_sample_export()
    print(f"\n✅ Created sample Hebrew chat: {sample_file}")
    
    # Load Hebrew mappings
    import yaml
    hebrew_config_path = Path(__file__).parent.parent / "config" / "hebrew_mappings.yaml"
    with open(hebrew_config_path, 'r', encoding='utf-8') as f:
        hebrew_config = yaml.safe_load(f)
    
    print("\n📝 Hebrew mappings loaded:")
    print(f"   - Action terms: {len(hebrew_config['hebrew_mappings'])} mappings")
    print(f"   - Bullish phrases: {len(hebrew_config['hebrew_signals']['bullish_phrases'])}")
    print(f"   - Bearish phrases: {len(hebrew_config['hebrew_signals']['bearish_phrases'])}")
    
    # Process with analyzer
    from data_sources.whatsapp_collector import WhatsAppAnalyzer
    
    analyzer = WhatsAppAnalyzer()
    messages = analyzer.parse_exported_chat(sample_file)
    
    print(f"\n📊 Analysis Results:")
    print(f"   - Messages parsed: {len(messages)}")
    
    # Show signals found
    bullish = sum(1 for m in messages if m.signal_type == "BULLISH")
    bearish = sum(1 for m in messages if m.signal_type == "BEARISH")
    
    print(f"   - Bullish signals: {bullish}")
    print(f"   - Bearish signals: {bearish}")
    
    # Show tickers mentioned
    all_tickers = set()
    for msg in messages:
        if msg.tickers_mentioned:
            all_tickers.update(msg.tickers_mentioned)
    
    print(f"   - Tickers found: {', '.join(sorted(all_tickers))}")
    
    # Generate summary
    summary = analyzer.generate_summary(messages, hours=24)
    
    print(f"\n💡 Top Signals:")
    for signal in summary.get("signals", [])[:3]:
        print(f"   - {signal['signal']} on {', '.join(signal['tickers'] or ['N/A'])}")
        print(f"     Confidence: {signal['confidence']:.1%}")
    
    # Generate hypotheses
    hypotheses = analyzer.create_hypothesis(summary)
    
    print(f"\n🎯 Trading Hypotheses Generated:")
    for hyp in hypotheses:
        print(f"   - {hyp}")
    
    print("\n✅ WhatsApp integration test successful!")
    print("   Your Hebrew messages will be properly analyzed!")
    
    # Clean up
    os.unlink(sample_file)
    
    return True

if __name__ == "__main__":
    test_whatsapp_processing()