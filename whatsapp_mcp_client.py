#!/usr/bin/env python3
"""
WhatsApp MCP Client for signal extraction and GitHub push
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
from pathlib import Path
import yaml

class WhatsAppSignalExtractor:
    """Extract trading signals from WhatsApp messages"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        self.config = self._load_config(config_path)
        self.signal_patterns = self._compile_patterns()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "whatsapp_config_private.yaml"
        
        if not Path(config_path).exists():
            # Use template config as fallback
            config_path = Path(__file__).parent / "config" / "whatsapp_config.template.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for signal detection"""
        patterns = {}
        
        # Build pattern for BUY signals
        buy_terms = '|'.join(self.config['signal_patterns']['buy_signals'])
        patterns['buy'] = re.compile(
            rf'\b({buy_terms})\b.*?([A-Z]{{2,5}})\b',
            re.IGNORECASE | re.UNICODE
        )
        
        # Build pattern for SELL signals
        sell_terms = '|'.join(self.config['signal_patterns']['sell_signals'])
        patterns['sell'] = re.compile(
            rf'\b({sell_terms})\b.*?([A-Z]{{2,5}})\b',
            re.IGNORECASE | re.UNICODE
        )
        
        # Pattern for price targets
        patterns['price'] = re.compile(
            r'\$?(\d+(?:\.\d+)?)',
            re.IGNORECASE
        )
        
        # Pattern for options (CALL/PUT)
        call_terms = '|'.join(self.config['signal_patterns']['call_options'])
        put_terms = '|'.join(self.config['signal_patterns']['put_options'])
        patterns['options'] = re.compile(
            rf'\b({call_terms}|{put_terms})\b',
            re.IGNORECASE | re.UNICODE
        )
        
        return patterns
    
    def extract_signals(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trading signals from WhatsApp messages"""
        signals = []
        
        for msg in messages:
            if not msg.get('message'):
                continue
            
            text = msg['message']
            timestamp = msg.get('timestamp', datetime.now().isoformat())
            sender = msg.get('sender', 'Unknown')
            
            # Check for BUY signals
            buy_match = self.signal_patterns['buy'].search(text)
            if buy_match:
                signal = self._create_signal(
                    'BUY', buy_match.group(2), text, timestamp, sender
                )
                if signal:
                    signals.append(signal)
            
            # Check for SELL signals
            sell_match = self.signal_patterns['sell'].search(text)
            if sell_match:
                signal = self._create_signal(
                    'SELL', sell_match.group(2), text, timestamp, sender
                )
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _create_signal(self, action: str, symbol: str, text: str, 
                      timestamp: str, sender: str) -> Optional[Dict[str, Any]]:
        """Create a structured signal from extracted data"""
        
        # Extract price if available
        price_match = self.signal_patterns['price'].search(text)
        price = float(price_match.group(1)) if price_match else None
        
        # Check for options
        options_match = self.signal_patterns['options'].search(text)
        option_type = None
        if options_match:
            term = options_match.group(1).upper()
            if term in [t.upper() for t in self.config['signal_patterns']['call_options']]:
                option_type = 'CALL'
            elif term in [t.upper() for t in self.config['signal_patterns']['put_options']]:
                option_type = 'PUT'
        
        # Calculate confidence based on trusted senders
        confidence = 0.8 if sender in self.config['trusted_senders'] else 0.5
        
        return {
            'timestamp': timestamp,
            'action': action,
            'symbol': symbol.upper(),
            'price': price,
            'option_type': option_type,
            'confidence': confidence,
            'source': 'whatsapp',
            'sender': self._anonymize_sender(sender),
            'original_text': text[:200]  # Truncate for privacy
        }
    
    def _anonymize_sender(self, sender: str) -> str:
        """Anonymize sender for privacy"""
        if sender in self.config['trusted_senders']:
            return f"trusted_{hash(sender) % 1000}"
        return f"user_{hash(sender) % 10000}"


class GitHubSignalPusher:
    """Push signals to GitHub repository"""
    
    def __init__(self, owner: str, repo: str, branch: str = "main"):
        """Initialize GitHub pusher"""
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.signals_dir = "whatsapp_signals"
    
    async def push_signals(self, signals: List[Dict[str, Any]], 
                          github_client) -> Dict[str, Any]:
        """Push signals to GitHub"""
        
        # Group signals by date
        signals_by_date = {}
        for signal in signals:
            date = signal['timestamp'].split('T')[0]
            if date not in signals_by_date:
                signals_by_date[date] = []
            signals_by_date[date].append(signal)
        
        results = []
        
        for date, date_signals in signals_by_date.items():
            # Create filename
            filename = f"{self.signals_dir}/{date}_signals.json"
            
            # Read existing signals if file exists
            existing_signals = []
            try:
                content = await github_client.get_file_contents(
                    owner=self.owner,
                    repo=self.repo,
                    path=filename,
                    branch=self.branch
                )
                if content:
                    existing_signals = json.loads(content)
            except:
                pass  # File doesn't exist yet
            
            # Merge signals (avoid duplicates)
            existing_hashes = {self._hash_signal(s) for s in existing_signals}
            new_signals = [s for s in date_signals 
                          if self._hash_signal(s) not in existing_hashes]
            
            if new_signals:
                all_signals = existing_signals + new_signals
                
                # Sort by timestamp
                all_signals.sort(key=lambda x: x['timestamp'])
                
                # Push to GitHub
                result = await github_client.create_or_update_file(
                    owner=self.owner,
                    repo=self.repo,
                    path=filename,
                    content=json.dumps(all_signals, indent=2),
                    message=f"Add {len(new_signals)} WhatsApp signals for {date}",
                    branch=self.branch
                )
                
                results.append({
                    'date': date,
                    'new_signals': len(new_signals),
                    'total_signals': len(all_signals),
                    'status': 'success' if result else 'failed'
                })
        
        return {
            'pushed_dates': len(results),
            'total_new_signals': sum(r['new_signals'] for r in results),
            'details': results
        }
    
    def _hash_signal(self, signal: Dict[str, Any]) -> str:
        """Create hash for signal to avoid duplicates"""
        key_parts = [
            signal.get('timestamp', ''),
            signal.get('action', ''),
            signal.get('symbol', ''),
            str(signal.get('price', '')),
            signal.get('sender', '')
        ]
        return '|'.join(key_parts)


async def process_whatsapp_export(export_path: str, github_client) -> Dict[str, Any]:
    """Process WhatsApp export and push signals to GitHub"""
    
    # Read WhatsApp export
    messages = []
    with open(export_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse messages (simple format)
    for line in lines:
        # Format: "DD/MM/YYYY, HH:MM - Sender: Message"
        match = re.match(
            r'(\d{1,2}/\d{1,2}/\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)',
            line
        )
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            sender = match.group(3).strip()
            message = match.group(4).strip()
            
            # Convert to ISO timestamp
            day, month, year = date_str.split('/')
            timestamp = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_str}:00"
            
            messages.append({
                'timestamp': timestamp,
                'sender': sender,
                'message': message
            })
    
    # Extract signals
    extractor = WhatsAppSignalExtractor()
    signals = extractor.extract_signals(messages)
    
    # Push to GitHub
    pusher = GitHubSignalPusher(
        owner="liorsolomon",
        repo="ai-options-trading-bot"
    )
    
    result = await pusher.push_signals(signals, github_client)
    
    return {
        'messages_processed': len(messages),
        'signals_extracted': len(signals),
        'github_push': result
    }


# Quick test function for Claude
async def quick_test():
    """Quick test to verify setup"""
    
    # Test signal extraction
    extractor = WhatsAppSignalExtractor()
    
    test_messages = [
        {
            'timestamp': '2024-08-15T10:30:00',
            'sender': 'TestUser',
            'message': 'BUY AAPL at $150'
        },
        {
            'timestamp': '2024-08-15T11:00:00',
            'sender': 'TestUser',
            'message': 'SELL TSLA CALL options'
        }
    ]
    
    signals = extractor.extract_signals(test_messages)
    
    print(f"Extracted {len(signals)} signals:")
    for signal in signals:
        print(f"  - {signal['action']} {signal['symbol']} "
              f"{'(' + signal['option_type'] + ')' if signal['option_type'] else ''}")
    
    return signals


if __name__ == "__main__":
    # Run quick test
    asyncio.run(quick_test())