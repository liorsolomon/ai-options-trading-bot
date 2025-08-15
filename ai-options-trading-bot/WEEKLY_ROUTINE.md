# 📱 Your 2-Minute Weekly Trading Routine

## 🎯 Every Monday Morning (or Sunday night)

### Step 1: Export WhatsApp Chat (30 seconds)
1. Open WhatsApp on your phone
2. Go to your **investChatIL** group
3. Tap the group name at top
4. Scroll down and tap **Export Chat**
5. Choose **Without Media** (important!)
6. Save to your computer via:
   - Email to yourself
   - AirDrop (iPhone → Mac)
   - Google Drive
   - USB cable

### Step 2: Upload to Bot (30 seconds)
Open Terminal in the bot folder and run:
```bash
# Activate environment
source venv/bin/activate

# Upload the chat export
python scripts/upload_whatsapp.py ~/Downloads/WhatsApp_Chat.txt
```

### Step 3: Push to GitHub (1 minute)
```bash
# Add files
git add whatsapp_data/

# Commit with date
git commit -m "WhatsApp signals $(date +%Y-%m-%d)"

# Push to GitHub
git push
```

### ✅ That's it! The bot now:
- Analyzes all messages from the past week
- Extracts trading signals and sentiment
- Uses Claude AI to evaluate opportunities
- Executes high-confidence trades automatically
- Sends you performance reports

---

## 📊 What Happens Next (Automatically)

### Within 5 minutes:
1. GitHub Actions detects your upload
2. Processes all messages
3. Identifies tickers mentioned (AAPL, SPY, NVDA, etc.)
4. Analyzes sentiment (bullish/bearish)
5. Detects Hebrew terms (קול → CALL, פוט → PUT)

### Within 10 minutes:
1. Claude AI evaluates each opportunity
2. Checks technical indicators
3. Assesses risk levels
4. Makes trading decisions

### Within 15 minutes:
1. Executes trades on Alpaca (paper trading)
2. Logs all decisions to database
3. Updates portfolio tracking
4. Generates performance report

---

## 📈 Check Your Results

### View Latest Analysis:
```bash
# See what signals were found
cat whatsapp_analysis/analysis_*.json | jq '.'

# Check bot logs
tail -f logs/trading_bot_*.log
```

### Monitor Performance:
```bash
# Run monitoring report
python -c "from src.monitoring.monitor import TradingMonitor; import asyncio; asyncio.run(TradingMonitor().generate_report())"
```

### View on GitHub:
- Go to Actions tab in your GitHub repo
- See "Process WhatsApp Signals" workflow
- Check "Trading Bot" workflow for executions

---

## 🔧 One-Time Setup (Already Done!)

✅ Anthropic API key configured
✅ Alpaca paper trading connected  
✅ Supabase database ready
✅ Hebrew language support added
✅ Privacy settings configured
✅ GitHub Actions workflows created

---

## 💡 Pro Tips

### Best Export Times:
- **Sunday Night**: Catch weekend discussions
- **Monday Morning**: Fresh week signals
- **Thursday Night**: Options expiry discussions

### Optimize Results:
1. Export during active discussion periods
2. Include at least 7 days of history
3. Export more frequently during volatile markets

### Privacy Maintained:
- ✅ Group name never stored
- ✅ Member names anonymized
- ✅ Only signals extracted
- ✅ Raw messages not kept

---

## 📱 Quick Mobile Shortcut (iOS)

Create a Shortcut on iPhone:
1. Open Shortcuts app
2. Create new shortcut
3. Add actions:
   - Open WhatsApp
   - Wait 2 seconds
   - Show notification "Export investChatIL chat"
4. Add to Home Screen
5. Run every Monday!

---

## 🚀 Start Now!

1. **Export your chat right now** (include last 7 days)
2. **Run the upload script**
3. **Push to GitHub**
4. **Watch the magic happen!**

Your first trades could execute within 15 minutes! 🎯

---

## ❓ Quick Troubleshooting

**File not found error?**
- Check the download location
- Rename file to remove spaces: `WhatsApp_Chat.txt`

**Hebrew text looks wrong?**
- File is UTF-8 encoded automatically
- Config handles Hebrew terms

**Want to test first?**
- Bot runs in simulation mode by default
- No real money at risk

**Need help?**
- Check `logs/` folder for details
- GitHub Actions tab shows workflow status