# 🤖 Automated WhatsApp Fetching with MCP

## ✅ Your WhatsApp MCP Server is Configured!

I found your WhatsApp MCP server at:
```
/Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server
```

## 🚀 Quick Start - Fetch WhatsApp Data Now

### Option 1: Using MCP Server (Automated)
```bash
# Test connection first
./scripts/test_mcp_connection.sh

# Fetch and process WhatsApp data
python scripts/fetch_whatsapp_mcp.py
```

This will:
1. Connect to your WhatsApp MCP server
2. Export investChatIL chat (last 7 days)
3. Analyze messages for trading signals
4. Push to GitHub
5. Trigger automatic trading

### Option 2: Manual Export (Backup)
```bash
# If MCP doesn't work, use manual export
./scripts/quick_upload.sh
```

## ⚙️ Set Up Automatic Fetching

### Create a Cron Job (Mac)
Run this every day at 9 AM:
```bash
# Open crontab
crontab -e

# Add this line:
0 9 * * * cd /Users/liorsolomon/Documents/Projects/ai-options-trading-bot/ai-options-trading-bot && /usr/bin/python3 scripts/fetch_whatsapp_mcp.py >> logs/whatsapp_fetch.log 2>&1
```

### Or Use macOS LaunchAgent
Create `~/Library/LaunchAgents/com.tradingbot.whatsapp.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tradingbot.whatsapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/liorsolomon/Documents/Projects/ai-options-trading-bot/ai-options-trading-bot/scripts/fetch_whatsapp_mcp.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/liorsolomon/Documents/Projects/ai-options-trading-bot/ai-options-trading-bot/logs/whatsapp.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.tradingbot.whatsapp.plist
```

## 📊 What Happens After Fetching

1. **Immediate (0-5 min):**
   - WhatsApp messages analyzed
   - Hebrew terms translated
   - Tickers extracted (AAPL, SPY, etc.)
   - Sentiment calculated

2. **GitHub Actions (5-10 min):**
   - Processes signals
   - Claude AI evaluates opportunities
   - Risk assessment performed

3. **Trading Execution (10-15 min):**
   - High-confidence trades executed
   - Positions opened on Alpaca
   - Performance tracked

## 🔧 Troubleshooting MCP Connection

If the MCP server doesn't work:

1. **Check if server is installed:**
   ```bash
   ls /Users/liorsolomon/mcp-servers/whatsapp-mcp/
   ```

2. **Install dependencies:**
   ```bash
   cd /Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server
   uv pip install -r requirements.txt
   ```

3. **Test manually:**
   ```bash
   /opt/homebrew/bin/uv --directory /Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server run main.py
   ```

4. **Fallback to manual:**
   ```bash
   # Export from WhatsApp manually, then:
   ./scripts/quick_upload.sh
   ```

## 📈 Monitor Your Bot

- **GitHub Actions:** https://github.com/[your-username]/ai-options-trading-bot/actions
- **Local logs:** `tail -f logs/trading_bot_*.log`
- **Performance:** `python scripts/show_performance.py`

## 🎯 You're All Set!

Your trading bot can now:
- ✅ Fetch WhatsApp data via MCP
- ✅ Analyze Hebrew messages
- ✅ Make AI-powered trades
- ✅ Run automatically

Just run: `python scripts/fetch_whatsapp_mcp.py` to start!