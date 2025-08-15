#!/bin/bash
# Quick WhatsApp Upload Script
# Makes the weekly routine even faster!

echo "📱 WhatsApp Trading Bot - Quick Upload"
echo "======================================"

# Activate virtual environment
source venv/bin/activate

# Find the latest WhatsApp export in Downloads
CHAT_FILE=$(ls -t ~/Downloads/*WhatsApp*.txt 2>/dev/null | head -1)

if [ -z "$CHAT_FILE" ]; then
    echo "❌ No WhatsApp export found in Downloads"
    echo "📝 Please export your chat first:"
    echo "   1. Open WhatsApp → investChatIL"
    echo "   2. Export Chat → Without Media"
    echo "   3. Save to Downloads"
    exit 1
fi

echo "✅ Found: $CHAT_FILE"

# Process the export
echo "🔄 Processing WhatsApp messages..."
python scripts/upload_whatsapp.py "$CHAT_FILE"

# Git operations
echo "📤 Pushing to GitHub..."
git add whatsapp_data/
git commit -m "WhatsApp signals $(date +%Y-%m-%d)"
git push

echo ""
echo "✅ SUCCESS! Your WhatsApp signals are uploaded!"
echo "⏰ GitHub Actions will process them in ~5 minutes"
echo ""
echo "📊 Check results at:"
echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo ""
echo "💡 Next upload: Same time next week!"