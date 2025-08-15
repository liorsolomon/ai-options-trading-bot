#!/usr/bin/env python3
"""
Fetch WhatsApp data using MCP Server
Connects to your configured WhatsApp MCP server
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class WhatsAppMCPClient:
    """Client to interact with WhatsApp MCP Server"""
    
    def __init__(self):
        # Your WhatsApp MCP server configuration
        self.command = "/opt/homebrew/bin/uv"
        self.args = [
            "--directory",
            "/Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server",
            "run",
            "main.py"
        ]
        self.data_dir = Path(__file__).parent.parent / "whatsapp_data"
        self.data_dir.mkdir(exist_ok=True)
        
    def fetch_latest_chat(self, group_name: str = "investChatIL") -> str:
        """
        Fetch latest chat export from WhatsApp MCP server
        
        Args:
            group_name: Name of the WhatsApp group
        """
        print(f"🔄 Connecting to WhatsApp MCP server...")
        print(f"   Looking for group: {group_name}")
        
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "export_chat",
                "arguments": {
                    "group": group_name,
                    "format": "txt",
                    "include_media": False,
                    "days": 7  # Last 7 days
                }
            },
            "id": 1
        }
        
        try:
            # Call MCP server with request
            process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send request and get response
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request),
                timeout=30
            )
            
            if process.returncode == 0:
                try:
                    response = json.loads(stdout)
                    if "result" in response:
                        return response["result"].get("content", "")
                    else:
                        print(f"❌ MCP error: {response.get('error', 'Unknown error')}")
                except json.JSONDecodeError:
                    # Maybe the server returns plain text
                    return stdout
            else:
                print(f"❌ Server error: {stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ MCP server timeout")
        except FileNotFoundError:
            print(f"❌ MCP server not found at: {self.command}")
            print("\n💡 Alternative: Try direct Python call")
            return self.fetch_direct()
        except Exception as e:
            print(f"❌ Error calling MCP server: {e}")
            
        return None
    
    def fetch_direct(self):
        """
        Try to call the MCP server directly with Python
        """
        try:
            # Try importing the MCP server directly
            mcp_path = "/Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server"
            sys.path.insert(0, mcp_path)
            
            # Import and call the main module
            import main
            
            # Check if it has an export function
            if hasattr(main, 'export_chat'):
                return main.export_chat("investChatIL", days=7)
            elif hasattr(main, 'get_chat_export'):
                return main.get_chat_export("investChatIL")
            else:
                print("❌ MCP server doesn't have expected export functions")
                
        except ImportError as e:
            print(f"❌ Cannot import MCP server: {e}")
        except Exception as e:
            print(f"❌ Error in direct call: {e}")
            
        return None
    
    def save_export(self, content: str) -> Path:
        """Save WhatsApp export to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_export_{timestamp}.txt"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Saved export: {filepath}")
        return filepath
    
    def process_and_push(self, filepath: Path):
        """Process the export and push to GitHub"""
        
        # Process with analyzer
        from data_sources.whatsapp_collector import process_whatsapp_export
        
        summary, hypotheses = process_whatsapp_export(str(filepath))
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total messages: {summary.get('total_messages', 0)}")
        print(f"   Bullish signals: {summary.get('bullish_signals', 0)}")
        print(f"   Bearish signals: {summary.get('bearish_signals', 0)}")
        print(f"   Top tickers: {', '.join([t[0] for t in summary.get('top_tickers', [])[:5]])}")
        print(f"   Hypotheses generated: {len(hypotheses)}")
        
        # Git operations
        print("\n📤 Pushing to GitHub...")
        os.system(f"git add {filepath}")
        os.system(f'git commit -m "MCP Auto: WhatsApp signals {datetime.now():%Y-%m-%d %H:%M}"')
        os.system("git push")
        
        print("\n✅ SUCCESS! GitHub Actions will process the signals!")
        print("   Check: https://github.com/YOUR_USERNAME/ai-options-trading-bot/actions")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🤖 WHATSAPP MCP INTEGRATION")
    print("="*60)
    
    client = WhatsAppMCPClient()
    
    # Try to fetch from MCP server
    print("\n📡 Fetching from WhatsApp MCP server...")
    content = client.fetch_latest_chat("investChatIL")
    
    if not content:
        print("\n❌ Could not fetch from MCP server")
        print("\n💡 Troubleshooting:")
        print("1. Make sure the MCP server is installed:")
        print("   cd /Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server")
        print("   uv pip install -r requirements.txt")
        print("\n2. Test the server manually:")
        print("   uv run main.py")
        print("\n3. Or use the manual export method:")
        print("   ./scripts/quick_upload.sh")
        return
    
    # Save and process
    filepath = client.save_export(content)
    client.process_and_push(filepath)
    
    print("\n🎯 Next steps:")
    print("1. Check GitHub Actions for processing")
    print("2. Monitor trades in the logs")
    print("3. Review performance reports")


if __name__ == "__main__":
    main()