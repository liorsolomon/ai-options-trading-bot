#!/usr/bin/env python3
"""
Automated WhatsApp Bridge
Connects to various sources to fetch WhatsApp data automatically
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class WhatsAppBridge:
    """
    Bridge to automatically fetch WhatsApp data from various sources
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "whatsapp_data"
        self.data_dir.mkdir(exist_ok=True)
        
    async def fetch_from_api(self, api_url: str, api_key: str) -> Optional[str]:
        """
        Fetch WhatsApp data from an API endpoint
        
        Args:
            api_url: Your WhatsApp data API endpoint
            api_key: Authentication key
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_as_whatsapp_export(data)
                    else:
                        print(f"❌ API error: {response.status}")
                        return None
            except Exception as e:
                print(f"❌ Connection error: {e}")
                return None
    
    async def fetch_from_cloud_storage(self, provider: str, credentials: Dict) -> Optional[str]:
        """
        Fetch from cloud storage (Google Drive, Dropbox, etc.)
        """
        if provider == "google_drive":
            return await self._fetch_google_drive(credentials)
        elif provider == "dropbox":
            return await self._fetch_dropbox(credentials)
        elif provider == "supabase":
            return await self._fetch_supabase(credentials)
        else:
            print(f"❌ Unsupported provider: {provider}")
            return None
    
    async def fetch_from_webhook(self, webhook_url: str) -> Optional[str]:
        """
        Fetch data posted to a webhook
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(webhook_url) as response:
                if response.status == 200:
                    return await response.text()
                return None
    
    def _format_as_whatsapp_export(self, messages: list) -> str:
        """
        Format messages as WhatsApp export format
        """
        export_lines = []
        
        for msg in messages:
            timestamp = msg.get("timestamp", datetime.now())
            sender = msg.get("sender", "Unknown")
            content = msg.get("content", "")
            
            # WhatsApp export format
            line = f"[{timestamp}] {sender}: {content}"
            export_lines.append(line)
        
        return "\n".join(export_lines)
    
    async def _fetch_google_drive(self, credentials: Dict) -> Optional[str]:
        """
        Fetch from Google Drive
        """
        # Implementation for Google Drive API
        # Requires google-api-python-client
        print("📁 Fetching from Google Drive...")
        # Add your implementation here
        return None
    
    async def _fetch_dropbox(self, credentials: Dict) -> Optional[str]:
        """
        Fetch from Dropbox
        """
        # Implementation for Dropbox API
        print("📁 Fetching from Dropbox...")
        # Add your implementation here
        return None
    
    async def _fetch_supabase(self, credentials: Dict) -> Optional[str]:
        """
        Fetch from Supabase storage
        """
        from supabase import create_client
        
        url = credentials.get("url")
        key = credentials.get("key")
        bucket = credentials.get("bucket", "whatsapp-exports")
        
        supabase = create_client(url, key)
        
        # Get latest file
        files = supabase.storage.from_(bucket).list()
        if files:
            latest = sorted(files, key=lambda x: x["created_at"])[-1]
            data = supabase.storage.from_(bucket).download(latest["name"])
            return data.decode("utf-8")
        
        return None
    
    async def save_export(self, content: str, source: str = "auto") -> str:
        """
        Save the fetched content as WhatsApp export
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_export_{source}_{timestamp}.txt"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Saved: {filepath}")
        return str(filepath)
    
    async def process_and_upload(self, content: str):
        """
        Process the export and trigger GitHub workflow
        """
        # Save the export
        filepath = await self.save_export(content)
        
        # Process with analyzer
        from data_sources.whatsapp_collector import process_whatsapp_export
        summary, hypotheses = process_whatsapp_export(filepath)
        
        print(f"📊 Found {len(hypotheses)} trading signals")
        
        # Commit to git (triggers GitHub Actions)
        os.system(f"git add {filepath}")
        os.system(f'git commit -m "Auto: WhatsApp signals {datetime.now():%Y-%m-%d %H:%M}"')
        os.system("git push")
        
        print("✅ Pushed to GitHub - Actions will process automatically!")


# Configuration for different sources
BRIDGE_CONFIG = {
    "mcp_server": {
        "enabled": False,
        "url": "http://localhost:3000/whatsapp",
        "api_key": "your_mcp_key"
    },
    "supabase": {
        "enabled": True,
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY"),
        "bucket": "whatsapp-exports"
    },
    "webhook": {
        "enabled": False,
        "url": "https://your-webhook.com/whatsapp"
    },
    "cloud_storage": {
        "enabled": False,
        "provider": "google_drive",
        "credentials": {}
    }
}


async def main():
    """
    Main automation routine
    """
    print("\n" + "="*60)
    print("🤖 WHATSAPP AUTOMATION BRIDGE")
    print("="*60)
    
    bridge = WhatsAppBridge()
    
    # Try different sources in order of preference
    content = None
    
    # 1. Try MCP Server (if you provide details)
    if BRIDGE_CONFIG["mcp_server"]["enabled"]:
        print("\n📡 Trying MCP Server...")
        content = await bridge.fetch_from_api(
            BRIDGE_CONFIG["mcp_server"]["url"],
            BRIDGE_CONFIG["mcp_server"]["api_key"]
        )
    
    # 2. Try Supabase
    if not content and BRIDGE_CONFIG["supabase"]["enabled"]:
        print("\n☁️ Trying Supabase...")
        content = await bridge.fetch_from_supabase(BRIDGE_CONFIG["supabase"])
    
    # 3. Try Webhook
    if not content and BRIDGE_CONFIG["webhook"]["enabled"]:
        print("\n🔗 Trying Webhook...")
        content = await bridge.fetch_from_webhook(BRIDGE_CONFIG["webhook"]["url"])
    
    # Process if we got content
    if content:
        print("\n✅ Successfully fetched WhatsApp data!")
        await bridge.process_and_upload(content)
    else:
        print("\n❌ No data sources available")
        print("\n💡 To connect your MCP server:")
        print("   1. Edit BRIDGE_CONFIG in this file")
        print("   2. Set mcp_server.enabled = True")
        print("   3. Add your MCP server URL and API key")
        print("   4. Run this script again")


if __name__ == "__main__":
    asyncio.run(main())