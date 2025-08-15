#!/usr/bin/env python3
"""
Upload WhatsApp export to cloud for processing
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
import shutil

def upload_whatsapp_export(file_path: str):
    """
    Process and upload WhatsApp export for GitHub Actions
    
    Usage:
        1. Export WhatsApp chat (without media)
        2. Run: python scripts/upload_whatsapp.py chat.txt
        3. GitHub Actions will process automatically
    """
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Create whatsapp_data directory
    data_dir = Path(__file__).parent.parent / "whatsapp_data"
    data_dir.mkdir(exist_ok=True)
    
    # Copy with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_file = data_dir / f"chat_export_{timestamp}.txt"
    
    shutil.copy(file_path, dest_file)
    print(f"✅ Copied to: {dest_file}")
    
    # Create metadata
    metadata = {
        "uploaded_at": datetime.now().isoformat(),
        "file_name": dest_file.name,
        "file_size": os.path.getsize(dest_file),
        "original_path": file_path
    }
    
    metadata_file = data_dir / f"metadata_{timestamp}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n📤 Next steps:")
    print("1. Commit and push to GitHub:")
    print(f"   git add whatsapp_data/")
    print(f"   git commit -m 'WhatsApp export {timestamp}'")
    print(f"   git push")
    print("\n2. GitHub Actions will automatically:")
    print("   - Analyze the messages")
    print("   - Extract trading signals")
    print("   - Make trading decisions")
    print("   - Execute trades if confident")
    
    return True


def setup_automation():
    """
    Set up automated WhatsApp processing
    """
    print("\n" + "="*60)
    print("🤖 WHATSAPP AUTOMATION SETUP")
    print("="*60)
    
    print("\n📱 CURRENT OPTIONS:\n")
    
    print("1️⃣  MANUAL EXPORT (Recommended to start)")
    print("   ✅ Works immediately")
    print("   ✅ No setup required")
    print("   ⏱️  Takes 2 minutes weekly")
    print("   📝 Steps:")
    print("      - Export chat from WhatsApp")
    print("      - Run: python scripts/upload_whatsapp.py chat.txt")
    print("      - Push to GitHub\n")
    
    print("2️⃣  CLOUD STORAGE SYNC")
    print("   ✅ Semi-automated")
    print("   📝 Steps:")
    print("      - Export to Google Drive/Dropbox")
    print("      - Set up sync to GitHub")
    print("      - Runs automatically\n")
    
    print("3️⃣  LOCAL BRIDGE (Advanced)")
    print("   ✅ Fully automated")
    print("   ⚠️  Requires always-on computer")
    print("   📝 We can set up:")
    print("      - WhatsApp Web scraper")
    print("      - Auto-upload to Supabase")
    print("      - GitHub reads from cloud\n")
    
    print("="*60)
    print("💡 RECOMMENDATION: Start with Option 1")
    print("   Test for 2 weeks, then automate if signals are profitable")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Upload file
        upload_whatsapp_export(sys.argv[1])
    else:
        # Show setup options
        setup_automation()
        print("\n📌 To upload a file:")
        print("   python scripts/upload_whatsapp.py <chat_export.txt>")