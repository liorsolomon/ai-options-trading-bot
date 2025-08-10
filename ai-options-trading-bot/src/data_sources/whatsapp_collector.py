"""
WhatsApp Group Data Collector
Collects and analyzes messages from configured WhatsApp groups
Privacy-preserving and configurable
"""

import json
import re
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib
from loguru import logger


@dataclass
class GroupMessage:
    """Represents a WhatsApp group message"""
    timestamp: datetime
    sender: str
    content: str
    message_type: str  # text, image, link
    
    # Analysis fields
    tickers_mentioned: List[str] = None
    sentiment: float = 0.0  # -1 to 1
    signal_type: Optional[str] = None  # BULLISH, BEARISH, NEUTRAL
    confidence: float = 0.0


class WhatsAppAnalyzer:
    """
    Analyzes WhatsApp messages for trading signals
    Designed to work with exported chat data
    Fully configurable for any group
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.data_dir = Path(__file__).parent.parent.parent / "whatsapp_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Use configured mappings or defaults
        self.custom_mappings = self.config.get("whatsapp", {}).get("custom_mappings", {})
        self.privacy_settings = self.config.get("whatsapp", {}).get("privacy", {
            "anonymize_senders": True,
            "hash_length": 8,
            "store_raw_messages": False
        })
        
        # Ticker patterns
        self.ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')
        self.option_pattern = re.compile(r'(CALL|PUT)', re.IGNORECASE)
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from file or use defaults"""
        if not config_path:
            config_path = Path(__file__).parent.parent.parent / "config" / "whatsapp_config.yaml"
        
        # If config file doesn't exist, use defaults
        if not Path(config_path).exists():
            logger.info("No config file found, using defaults")
            return {
                "whatsapp": {
                    "group_name": "Investment Group",
                    "analysis": {
                        "default_lookback_hours": 168,
                        "min_confidence_threshold": 0.7
                    },
                    "privacy": {
                        "anonymize_senders": True,
                        "hash_length": 8,
                        "store_raw_messages": False
                    }
                }
            }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Could not load config: {e}, using defaults")
            return {"whatsapp": {}}
        
    def parse_exported_chat(self, file_path: str) -> List[GroupMessage]:
        """
        Parse WhatsApp exported chat file
        Export format: [date, time] sender: message
        """
        messages = []
        
        # Pattern for WhatsApp export format
        # Example: [8/10/24, 14:27:35] John Doe: Buy SPY calls
        pattern = r'\[(\d+/\d+/\d+), (\d+:\d+:\d+)\] ([^:]+): (.+)'
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for match in matches:
            date_str, time_str, sender, message = match
            
            # Parse timestamp
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M:%S")
            
            # Create message object
            msg = GroupMessage(
                timestamp=timestamp,
                sender=sender.strip(),
                content=message.strip(),
                message_type="text"
            )
            
            # Analyze message
            msg = self.analyze_message(msg)
            messages.append(msg)
        
        logger.info(f"Parsed {len(messages)} messages from WhatsApp export")
        return messages
    
    def analyze_message(self, msg: GroupMessage) -> GroupMessage:
        """Analyze a single message for trading signals"""
        
        # Extract tickers
        msg.tickers_mentioned = self.extract_tickers(msg.content)
        
        # Analyze sentiment
        msg.sentiment = self.calculate_sentiment(msg.content)
        
        # Determine signal type
        msg.signal_type = self.determine_signal(msg.content)
        
        # Calculate confidence based on message characteristics
        msg.confidence = self.calculate_confidence(msg)
        
        return msg
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from message"""
        tickers = self.ticker_pattern.findall(text)
        
        # Filter common words that match pattern but aren't tickers
        excluded = ['I', 'A', 'THE', 'AND', 'OR', 'IF', 'IN', 'ON', 'AT', 'TO']
        tickers = [t for t in tickers if t not in excluded]
        
        # Add custom ticker mappings from config
        custom_tickers = self.custom_mappings.get("ticker_mappings", {})
        for custom_term, ticker in custom_tickers.items():
            if custom_term in text:
                tickers.append(ticker)
        
        return list(set(tickers))  # Remove duplicates
    
    def calculate_sentiment(self, text: str) -> float:
        """Calculate message sentiment"""
        
        # Get configured terms or use defaults
        bullish = self.custom_mappings.get("bullish_terms", 
            ['buy', 'call', 'long', 'bullish', 'up', 'rising', 'strong', 'breakout'])
        
        bearish = self.custom_mappings.get("bearish_terms",
            ['sell', 'put', 'short', 'bearish', 'down', 'falling', 'weak', 'breakdown'])
        
        text_lower = text.lower()
        
        bullish_count = sum(1 for word in bullish if word in text_lower)
        bearish_count = sum(1 for word in bearish if word in text_lower)
        
        if bullish_count + bearish_count == 0:
            return 0.0
        
        sentiment = (bullish_count - bearish_count) / (bullish_count + bearish_count)
        return max(-1.0, min(1.0, sentiment))
    
    def determine_signal(self, text: str) -> str:
        """Determine if message contains trading signal"""
        
        if self.option_pattern.search(text):
            if "call" in text.lower() or "קול" in text:
                return "BULLISH"
            elif "put" in text.lower() or "פוט" in text:
                return "BEARISH"
        
        sentiment = self.calculate_sentiment(text)
        
        if sentiment > 0.3:
            return "BULLISH"
        elif sentiment < -0.3:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def calculate_confidence(self, msg: GroupMessage) -> float:
        """Calculate confidence score for message"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence for specific patterns
        if msg.tickers_mentioned:
            confidence += 0.1
        
        if abs(msg.sentiment) > 0.5:
            confidence += 0.15
        
        # Check for price targets or specific levels
        if re.search(r'\$?\d+\.?\d*', msg.content):
            confidence += 0.1
        
        # Check for options terminology
        if self.option_pattern.search(msg.content):
            confidence += 0.15
        
        return min(1.0, confidence)
    
    def generate_summary(self, messages: List[GroupMessage], hours: int = 24) -> Dict[str, Any]:
        """Generate summary of recent messages"""
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_messages = [m for m in messages if m.timestamp > cutoff]
        
        if not recent_messages:
            return {"error": "No recent messages"}
        
        # Aggregate tickers mentioned
        ticker_counts = {}
        for msg in recent_messages:
            for ticker in msg.tickers_mentioned or []:
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        # Sort by frequency
        top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Aggregate sentiment
        bullish_msgs = [m for m in recent_messages if m.signal_type == "BULLISH"]
        bearish_msgs = [m for m in recent_messages if m.signal_type == "BEARISH"]
        
        # Calculate overall sentiment
        avg_sentiment = sum(m.sentiment for m in recent_messages) / len(recent_messages)
        
        # High confidence signals
        high_confidence = [m for m in recent_messages if m.confidence > 0.7]
        
        summary = {
            "period_hours": hours,
            "total_messages": len(recent_messages),
            "unique_senders": len(set(m.sender for m in recent_messages)),
            "top_tickers": top_tickers,
            "bullish_signals": len(bullish_msgs),
            "bearish_signals": len(bearish_msgs),
            "overall_sentiment": avg_sentiment,
            "high_confidence_signals": len(high_confidence),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add specific high confidence signals
        if high_confidence:
            summary["signals"] = []
            for msg in high_confidence[:5]:  # Top 5
                summary["signals"].append({
                    "time": msg.timestamp.isoformat(),
                    "sender": self.anonymize_sender(msg.sender),
                    "tickers": msg.tickers_mentioned,
                    "signal": msg.signal_type,
                    "confidence": msg.confidence,
                    "preview": msg.content[:100]  # First 100 chars
                })
        
        return summary
    
    def anonymize_sender(self, sender: str) -> str:
        """Anonymize sender name for privacy"""
        return hashlib.md5(sender.encode()).hexdigest()[:8]
    
    def create_hypothesis(self, summary: Dict[str, Any]) -> List[str]:
        """Generate testable hypotheses from group insights"""
        
        hypotheses = []
        
        # Hypothesis based on most mentioned tickers
        if summary.get("top_tickers"):
            top_ticker = summary["top_tickers"][0][0]
            hypotheses.append(
                f"High group interest in {top_ticker} correlates with price movement"
            )
        
        # Hypothesis based on sentiment
        if summary.get("overall_sentiment", 0) > 0.3:
            hypotheses.append(
                "Bullish group sentiment precedes market upward movement"
            )
        elif summary.get("overall_sentiment", 0) < -0.3:
            hypotheses.append(
                "Bearish group sentiment precedes market downward movement"
            )
        
        # Hypothesis based on consensus
        if summary.get("bullish_signals", 0) > summary.get("bearish_signals", 0) * 2:
            hypotheses.append(
                "Strong bullish consensus in group leads to profitable CALL options"
            )
        
        return hypotheses


def process_whatsapp_export(file_path: str):
    """Process WhatsApp export file and generate insights"""
    
    analyzer = WhatsAppAnalyzer()
    
    # Parse messages
    messages = analyzer.parse_exported_chat(file_path)
    
    # Generate summary
    summary = analyzer.generate_summary(messages, hours=24)
    
    # Generate hypotheses
    hypotheses = analyzer.create_hypothesis(summary)
    
    print("\n" + "="*60)
    print("📱 WHATSAPP GROUP ANALYSIS")
    print("="*60)
    
    print(f"\n📊 Summary (Last 24 Hours):")
    print(f"   Messages: {summary.get('total_messages', 0)}")
    print(f"   Active Members: {summary.get('unique_senders', 0)}")
    print(f"   Bullish Signals: {summary.get('bullish_signals', 0)}")
    print(f"   Bearish Signals: {summary.get('bearish_signals', 0)}")
    print(f"   Overall Sentiment: {summary.get('overall_sentiment', 0):.2f}")
    
    if summary.get("top_tickers"):
        print(f"\n🎯 Most Discussed Tickers:")
        for ticker, count in summary["top_tickers"][:5]:
            print(f"   {ticker}: {count} mentions")
    
    if hypotheses:
        print(f"\n💡 Generated Hypotheses:")
        for i, hyp in enumerate(hypotheses, 1):
            print(f"   {i}. {hyp}")
    
    # Save summary
    output_file = Path(file_path).parent / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n✅ Analysis saved to: {output_file}")
    
    return summary, hypotheses


if __name__ == "__main__":
    # Example usage
    print("""
    To use this analyzer:
    
    1. Export WhatsApp chat:
       - Open WhatsApp group
       - Click menu → More → Export chat
       - Choose "Without media"
       - Save the .txt file
    
    2. Run analysis:
       python src/data_sources/whatsapp_collector.py path/to/chat.txt
    """)
    
    # If file provided as argument
    import sys
    if len(sys.argv) > 1:
        process_whatsapp_export(sys.argv[1])