#!/usr/bin/env python3
"""
WhatsApp MCP Client - Properly communicates with MCP server
Uses the MCP protocol to fetch WhatsApp data
"""

import json
import subprocess
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class MCPClient:
    """MCP Protocol Client for WhatsApp Server"""
    
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
        self.process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the connection
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "tools": {},
                    "prompts": {}
                }
            },
            "id": self.get_request_id()
        })
        
        response = await self.read_response()
        if response and "result" in response:
            print("✅ MCP server initialized")
            return True
        return False
    
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
                return json.loads(line.decode())
        except asyncio.TimeoutError:
            print("⏱️ Response timeout")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
        return None
    
    async def list_tools(self):
        """List available tools from the MCP server"""
        print("\n🔧 Listing available tools...")
        
        await self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self.get_request_id()
        })
        
        response = await self.read_response()
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"📋 Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name')}: {tool.get('description', 'No description')}")
            return tools
        return []
    
    async def export_chat(self, group_name: str = "investChatIL", days: int = 7):
        """Export WhatsApp chat using MCP server"""
        print(f"\n📱 Exporting WhatsApp chat: {group_name} (last {days} days)")
        
        # Try different possible tool names
        tool_names = [
            "export_chat",
            "get_chat_history", 
            "fetch_messages",
            "read_chat",
            "get_messages"
        ]
        
        for tool_name in tool_names:
            print(f"   Trying tool: {tool_name}")
            
            await self.send_request({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": {
                        "group": group_name,
                        "group_name": group_name,
                        "chat": group_name,
                        "days": days,
                        "format": "txt",
                        "include_media": False
                    }
                },
                "id": self.get_request_id()
            })
            
            response = await self.read_response(timeout=10.0)
            if response:
                if "result" in response:
                    content = response["result"].get("content")
                    if content:
                        print(f"✅ Successfully exported using {tool_name}")
                        return content
                elif "error" in response:
                    error = response["error"]
                    if "not found" not in str(error).lower():
                        print(f"   Error: {error.get('message', error)}")
        
        return None
    
    async def close(self):
        """Close the MCP server connection"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("🔌 MCP server closed")


async def fetch_whatsapp_data():
    """Main function to fetch WhatsApp data via MCP"""
    
    print("\n" + "="*60)
    print("🤖 WHATSAPP MCP CLIENT")
    print("="*60)
    
    client = MCPClient()
    
    try:
        # Start the MCP server
        if not await client.start():
            print("❌ Failed to initialize MCP server")
            print("\n💡 Fallback: Use manual export")
            print("   1. Export from WhatsApp")
            print("   2. Run: ./scripts/quick_upload.sh")
            return None
        
        # List available tools
        tools = await client.list_tools()
        
        # Try to export chat
        content = await client.export_chat("investChatIL", days=7)
        
        if content:
            # Save the export
            data_dir = Path(__file__).parent.parent / "whatsapp_data"
            data_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = data_dir / f"mcp_export_{timestamp}.txt"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ Saved export: {filepath}")
            
            # Process with analyzer
            from data_sources.whatsapp_collector import process_whatsapp_export
            summary, hypotheses = process_whatsapp_export(str(filepath))
            
            print(f"\n📊 Analysis Results:")
            print(f"   Messages: {summary.get('total_messages', 0)}")
            print(f"   Signals: {len(hypotheses)}")
            
            # Git push
            import os
            os.system(f"git add {filepath}")
            os.system(f'git commit -m "MCP: WhatsApp export {timestamp}"')
            os.system("git push")
            
            print("\n✅ SUCCESS! Pushed to GitHub")
            return filepath
        else:
            print("\n❌ Could not export chat")
            print("The MCP server may not have WhatsApp access configured")
            
    finally:
        await client.close()
    
    return None


def main():
    """Entry point"""
    result = asyncio.run(fetch_whatsapp_data())
    
    if not result:
        print("\n" + "="*60)
        print("📝 MANUAL EXPORT INSTRUCTIONS")
        print("="*60)
        print("\n1. Open WhatsApp on your phone")
        print("2. Go to investChatIL group")
        print("3. Export Chat → Without Media")
        print("4. Save to Downloads")
        print("5. Run: ./scripts/quick_upload.sh")
        print("\nThis takes just 2 minutes and works every time!")


if __name__ == "__main__":
    main()