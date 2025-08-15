#!/usr/bin/env python3
"""
Working WhatsApp MCP Integration
Uses the actual MCP server tools: list_chats and list_messages
"""

import json
import subprocess
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class WhatsAppMCPWorking:
    """Working MCP Client that uses the actual WhatsApp tools"""
    
    def __init__(self):
        self.command = "/opt/homebrew/bin/uv"
        self.args = [
            "--directory",
            "/Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server",
            "run",
            "main.py"
        ]
        self.process = None
        self.request_id = 0
        
    async def start(self):
        """Start the MCP server process"""
        print("🚀 Starting WhatsApp MCP server...")
        
        # Start the process
        self.process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a moment for server to start
        await asyncio.sleep(1)
        
        # Send initialization
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "tools": {}
                }
            },
            "id": self.get_request_id()
        })
        
        # Try to read response (may timeout, that's OK)
        response = await self.read_response(timeout=2.0)
        if response:
            print("✅ MCP server responded")
        else:
            print("⚠️ No initialization response (server may still be working)")
        
        return True
    
    def get_request_id(self):
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def send_request(self, request: Dict):
        """Send a request to the MCP server"""
        if not self.process:
            return None
            
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
    async def read_response(self, timeout: float = 5.0):
        """Read response from MCP server"""
        if not self.process:
            return None
            
        try:
            line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=timeout
            )
            if line:
                return json.loads(line.decode().strip())
        except asyncio.TimeoutError:
            return None
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"Read error: {e}")
            return None
    
    async def find_invest_chat(self):
        """Find the investChatIL chat"""
        print("\n🔍 Looking for investChatIL chat...")
        
        # List all chats
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_chats",
                "arguments": {
                    "query": "invest",
                    "limit": 50,
                    "include_last_message": True
                }
            },
            "id": self.get_request_id()
        })
        
        response = await self.read_response(timeout=10.0)
        if response and "result" in response:
            chats = response["result"].get("content", [])
            
            # Look for investChatIL or similar
            for chat in chats:
                chat_name = chat.get("name", "").lower()
                if "invest" in chat_name or "chat" in chat_name:
                    print(f"✅ Found chat: {chat.get('name')} (JID: {chat.get('jid')})")
                    return chat.get("jid")
        
        print("❌ investChatIL chat not found")
        print("\n💡 Available chats:")
        
        # Try listing all chats without filter
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_chats",
                "arguments": {
                    "limit": 20
                }
            },
            "id": self.get_request_id()
        })
        
        response = await self.read_response(timeout=10.0)
        if response and "result" in response:
            chats = response["result"].get("content", [])
            for chat in chats[:10]:
                print(f"   - {chat.get('name', 'Unknown')}")
        
        return None
    
    async def get_messages(self, chat_jid: Optional[str] = None, days: int = 7):
        """Get messages from WhatsApp"""
        print(f"\n📱 Fetching messages from last {days} days...")
        
        # Calculate date range
        after_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Request messages
        request_params = {
            "after": after_date,
            "limit": 1000,
            "include_context": True
        }
        
        if chat_jid:
            request_params["chat_jid"] = chat_jid
        
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_messages",
                "arguments": request_params
            },
            "id": self.get_request_id()
        })
        
        response = await self.read_response(timeout=15.0)
        if response and "result" in response:
            messages = response["result"].get("content", [])
            print(f"✅ Retrieved {len(messages)} messages")
            return messages
        
        return []
    
    def format_as_whatsapp_export(self, messages: List[Dict]) -> str:
        """Format messages as WhatsApp export format"""
        lines = []
        
        for msg in messages:
            # Extract fields
            timestamp = msg.get("timestamp", "")
            sender = msg.get("sender", {}).get("name", "Unknown")
            content = msg.get("content", "")
            
            # Format as WhatsApp export
            # [10/08/24, 09:30:15] Sender: Message
            if timestamp and content:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("[%d/%m/%y, %H:%M:%S]")
                    lines.append(f"{formatted_time} {sender}: {content}")
                except:
                    lines.append(f"[{timestamp}] {sender}: {content}")
        
        return "\n".join(lines)
    
    async def close(self):
        """Close the MCP server"""
        if self.process:
            self.process.terminate()
            await asyncio.sleep(0.5)
            if self.process.returncode is None:
                self.process.kill()
            print("🔌 MCP server closed")


async def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🤖 WHATSAPP MCP FETCH (WORKING VERSION)")
    print("="*60)
    
    client = WhatsAppMCPWorking()
    
    try:
        # Start server
        await client.start()
        
        # Find investChatIL
        chat_jid = await client.find_invest_chat()
        
        # Get messages
        messages = await client.get_messages(chat_jid, days=7)
        
        if messages:
            # Format as WhatsApp export
            export_content = client.format_as_whatsapp_export(messages)
            
            # Save to file
            data_dir = Path(__file__).parent.parent / "whatsapp_data"
            data_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = data_dir / f"mcp_messages_{timestamp}.txt"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            print(f"\n✅ Saved {len(messages)} messages to: {filepath}")
            
            # Process with analyzer
            from data_sources.whatsapp_collector import process_whatsapp_export
            summary, hypotheses = process_whatsapp_export(str(filepath))
            
            print(f"\n📊 Analysis Results:")
            print(f"   Total messages: {summary.get('total_messages', 0)}")
            print(f"   Bullish signals: {summary.get('bullish_signals', 0)}")
            print(f"   Bearish signals: {summary.get('bearish_signals', 0)}")
            
            if summary.get("top_tickers"):
                print(f"   Top tickers: {', '.join([t[0] for t in summary['top_tickers'][:5]])}")
            
            print(f"   Trading hypotheses: {len(hypotheses)}")
            
            # Git push
            import os
            os.system(f"git add {filepath}")
            os.system(f'git commit -m "MCP: WhatsApp messages {timestamp}"')
            os.system("git push")
            
            print("\n✅ SUCCESS! Pushed to GitHub - bot will trade automatically!")
            
        else:
            print("\n❌ No messages retrieved")
            print("\n💡 The MCP server may need WhatsApp Web to be connected")
            print("   1. Make sure WhatsApp Web is logged in")
            print("   2. Or use manual export: ./scripts/quick_upload.sh")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Use manual export as fallback:")
        print("   ./scripts/quick_upload.sh")
        
    finally:
        await client.close()


if __name__ == "__main__":
    # Run the async main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")