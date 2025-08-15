#!/usr/bin/env python3
"""
Connect to WhatsApp MCP Server
Fetches chat exports automatically
"""

import json
import subprocess
import sys
from pathlib import Path

def setup_mcp_connection():
    """
    Setup connection to WhatsApp MCP server
    """
    print("\n" + "="*60)
    print("🔌 WHATSAPP MCP SERVER CONNECTION")
    print("="*60)
    
    print("\nTo connect your WhatsApp MCP server, I need:")
    print("1. The path to your MCP server script")
    print("2. The Python interpreter path (if using venv)")
    print("3. Any required arguments")
    
    print("\n📝 Example MCP config:")
    example = {
        "mcpServers": {
            "whatsapp": {
                "command": "/path/to/venv/bin/python",
                "args": ["/path/to/whatsapp_mcp_server.py"]
            }
        }
    }
    print(json.dumps(example, indent=2))
    
    print("\n💡 If you have this in your Claude Desktop config,")
    print("   copy it here or run:")
    print("   cp ~/Library/Application\\ Support/Claude/claude_desktop_config.json .")
    
    # Check if config was copied
    local_config = Path("claude_desktop_config.json")
    if local_config.exists():
        with open(local_config, 'r') as f:
            config = json.load(f)
            
        if "mcpServers" in config:
            for server_name, server_config in config["mcpServers"].items():
                if "whatsapp" in server_name.lower():
                    print(f"\n✅ Found WhatsApp MCP server: {server_name}")
                    print(f"   Command: {server_config.get('command')}")
                    print(f"   Args: {server_config.get('args')}")
                    
                    return server_config
    
    return None

def call_mcp_server(config):
    """
    Call the MCP server to get WhatsApp data
    """
    if not config:
        print("❌ No MCP server config found")
        return None
        
    command = config.get("command", "python")
    args = config.get("args", [])
    
    try:
        # Call the MCP server
        result = subprocess.run(
            [command] + args + ["--export-latest"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"❌ MCP server error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to call MCP server: {e}")
        return None

def save_and_process(content):
    """
    Save WhatsApp export and trigger processing
    """
    if not content:
        return
        
    # Save to whatsapp_data
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    data_dir = Path(__file__).parent.parent / "whatsapp_data"
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / f"mcp_export_{timestamp}.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Saved export: {filepath}")
    
    # Process with analyzer
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from data_sources.whatsapp_collector import process_whatsapp_export
    
    summary, hypotheses = process_whatsapp_export(str(filepath))
    
    print(f"\n📊 Analysis Results:")
    print(f"   Messages: {summary.get('total_messages', 0)}")
    print(f"   Signals: {len(hypotheses)}")
    
    # Git push to trigger GitHub Actions
    import os
    os.system(f"git add {filepath}")
    os.system(f'git commit -m "MCP: WhatsApp export {timestamp}"')
    os.system("git push")
    
    print("\n✅ Pushed to GitHub - bot will process automatically!")

if __name__ == "__main__":
    # Setup and connect
    config = setup_mcp_connection()
    
    if config:
        print("\n🔄 Fetching WhatsApp data from MCP server...")
        content = call_mcp_server(config)
        
        if content:
            save_and_process(content)
    else:
        print("\n📋 Manual setup needed:")
        print("1. Copy your Claude config here:")
        print("   cp ~/Library/Application\\ Support/Claude/claude_desktop_config.json .")
        print("2. Run this script again")
        print("\nOR provide your MCP server details manually")