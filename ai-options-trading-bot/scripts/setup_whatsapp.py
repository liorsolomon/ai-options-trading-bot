#!/usr/bin/env python3
"""
Setup WhatsApp integration with privacy
"""

import shutil
from pathlib import Path


def setup_whatsapp_config():
    """Setup private WhatsApp configuration"""
    
    print("\n" + "="*60)
    print("🔐 WHATSAPP PRIVACY SETUP")
    print("="*60)
    
    template_path = Path(__file__).parent.parent / "config" / "whatsapp_config.template.yaml"
    private_path = Path(__file__).parent.parent / "config" / "whatsapp_config_private.yaml"
    
    if private_path.exists():
        print("\n⚠️  Private config already exists!")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled")
            return
    
    # Copy template
    shutil.copy(template_path, private_path)
    print(f"\n✅ Created private config: {private_path}")
    
    print("\n📝 Next steps:")
    print("1. Edit config/whatsapp_config_private.yaml")
    print("2. Add your group's specific terms and mappings")
    print("3. The private file will NOT be uploaded to GitHub")
    
    print("\n🔒 Privacy features:")
    print("• All sender names are anonymized")
    print("• No group names in code")
    print("• Raw messages not stored")
    print("• Config file ignored by git")
    
    print("\n📱 To analyze your group:")
    print("1. Export WhatsApp chat (without media)")
    print("2. Run: python scripts/analyze_whatsapp.py <chat.txt>")
    print("3. Check whatsapp_analysis/ for results")
    
    # Create directories
    dirs = [
        Path(__file__).parent.parent / "whatsapp_data",
        Path(__file__).parent.parent / "whatsapp_analysis"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)
    
    print("\n✅ Setup complete! Your group data will remain private.")


if __name__ == "__main__":
    setup_whatsapp_config()