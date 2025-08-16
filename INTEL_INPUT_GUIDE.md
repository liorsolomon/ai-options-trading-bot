# 📊 COMPLETE GUIDE: How to Provide Intel to Your Trading Bot

## Option 1: JSON Signal Files (RECOMMENDED - Most Precise)

**Location:** `/signals/` folder  
**File Format:** `any_name.json`  
**Priority:** HIGHEST - These are processed first

### Example Structure:
```json
{
  "timestamp": "2025-08-16T09:00:00Z",
  "source": "your_analysis_source",
  "signals": [
    {
      "ticker": "AAPL",
      "action": "BUY_CALL",
      "strike": 180.0,
      "expiration_days": 30,
      "confidence": 0.85,
      "reasoning": "Strong earnings, iPhone 16 launch",
      "risk_level": "LOW"
    },
    {
      "ticker": "NVDA",
      "action": "BUY_PUT",
      "strike": 800.0,
      "expiration_days": 45,
      "confidence": 0.65,
      "reasoning": "Overbought, due for correction",
      "risk_level": "MEDIUM"
    }
  ],
  "market_context": {
    "overall_sentiment": "bullish",
    "key_events": ["Fed meeting Sept 15", "Earnings season"],
    "risk_factors": ["Inflation data", "China tensions"]
  }
}
```

### How to Use:
1. Create a new `.json` file in `/signals/` folder
2. Add your trading signals using the structure above
3. Bot will automatically read on next run
4. These signals get HIGHEST priority

---

## Option 2: WhatsApp Export Format (Natural Language)

**Location:** `/whatsapp_data/` folder  
**File Format:** `.txt` file mimicking WhatsApp export  
**Priority:** MEDIUM - Processed after JSON signals

### Example Structure:
```
[8/16/25, 09:00:00] Analyst: 🚀 BULLISH on AAPL
Looking at strong iPhone 16 pre-orders. Technical breakout above $175.
Buy CALL AAPL $180 September expiry
Target: $190, Stop: $170

[8/16/25, 09:05:00] Trader: Agreed on AAPL. Also watching TSLA
Tesla showing cup and handle formation. 
Buy CALL TSLA $250 October

[8/16/25, 09:10:00] Expert: ⚠️ BEARISH on RIVN
Competition increasing, cash burn high
Buy PUT RIVN $15 September
```

### How to Use:
1. Create a `.txt` file in `/whatsapp_data/` folder
2. Use WhatsApp chat export format: `[date, time] Name: message`
3. Include tickers in CAPS
4. Mention CALL/PUT explicitly
5. Bot extracts tickers and sentiment automatically

---

## Option 3: Direct GitHub Actions Secrets (Environment Variables)

**Location:** GitHub Settings → Secrets → Actions  
**Format:** Key-value pairs  
**Priority:** Used for API keys and configuration

### Current Secrets:
- `ANTHROPIC_API_KEY` - Claude AI access
- `ALPACA_API_KEY` - Trading platform
- `DATABASE_URL` - Supabase connection

### How to Add Trading Signals via Secrets:
1. Go to: https://github.com/[your-username]/ai-options-trading-bot/settings/secrets/actions
2. Add new secret: `TRADING_SIGNALS`
3. Value: JSON string of signals
4. Reference in workflow: `${{ secrets.TRADING_SIGNALS }}`

---

## Option 4: Pull Request with Signals (Automated)

**Location:** GitHub Pull Requests  
**Format:** YAML in PR description  
**Priority:** Triggers automatic workflow

### Example PR Description:
```yaml
signals:
  - ticker: AAPL
    action: BUY_CALL
    strike: 180
    confidence: 0.85
  - ticker: GOOGL
    action: BUY_PUT
    strike: 140
    confidence: 0.70
```

### How to Use:
1. Create branch: `signals-YYYYMMDD-HHMMSS`
2. Add signal file
3. Open PR with YAML in description
4. Bot processes automatically

---

## Option 5: Supabase Database (Direct Insert)

**Location:** Supabase Dashboard  
**Format:** Database records  
**Priority:** Real-time processing

### Table Structure:
```sql
-- trading_signals table
INSERT INTO trading_signals (
  ticker,
  signal_type,
  confidence,
  source,
  metadata,
  created_at
) VALUES (
  'AAPL',
  'BUY_CALL',
  0.85,
  'manual_analysis',
  '{"strike": 180, "expiration_days": 30}',
  NOW()
);
```

### How to Use:
1. Login to Supabase dashboard
2. Navigate to Table Editor → trading_signals
3. Insert new row with signal data
4. Bot reads on next cycle

---

## Option 6: Local Testing (Development)

**Location:** Local files on your machine  
**Format:** Python scripts or JSON  
**Priority:** Immediate execution

### Quick Test Script:
```python
# test_signal.py
import json

signal = {
    "ticker": "AAPL",
    "action": "BUY_CALL",
    "strike": 180.0,
    "confidence": 0.85
}

with open('signals/test_signal.json', 'w') as f:
    json.dump({"signals": [signal]}, f)

print("Signal saved! Run the bot to process.")
```

---

## Option 7: API Endpoint (Future Enhancement)

**Location:** Not yet implemented  
**Format:** HTTP POST requests  
**Priority:** Would be real-time

### Potential Structure:
```bash
curl -X POST https://your-bot-api.com/signals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ticker": "AAPL",
    "action": "BUY_CALL",
    "strike": 180,
    "confidence": 0.85
  }'
```

---

## 🎯 QUICK DECISION GUIDE

### Use JSON Signals When:
- You have specific strikes/expirations in mind
- You want precise control over trades
- You're providing multiple signals at once
- You need highest priority processing

### Use WhatsApp Format When:
- You have natural language analysis
- You're copying from actual chat discussions
- You want the bot to extract sentiment
- You prefer conversational format

### Use GitHub Secrets When:
- Setting API keys or credentials
- Configuring bot parameters
- Storing sensitive information

### Use Database When:
- You need real-time updates
- You want historical tracking
- Multiple sources provide signals
- You need complex queries

---

## 📁 FILE LOCATIONS SUMMARY

```
ai-options-trading-bot/
├── signals/                    # JSON signal files (HIGH PRIORITY)
│   ├── daily_analysis.json
│   ├── crypto_signals.json
│   └── momentum_trades.json
├── whatsapp_data/              # WhatsApp export format (MEDIUM PRIORITY)
│   ├── chat_export_20250816.txt
│   └── manual_analysis.txt
├── src/
│   └── main.py                 # Reads signals from above folders
└── .github/
    └── workflows/
        └── trading-bot.yml     # Uses GitHub Secrets
```

---

## 🚀 QUICKSTART EXAMPLE

### Step 1: Create Your Signal File
```bash
# Create signals folder if it doesn't exist
mkdir -p signals

# Create your signal file
cat > signals/my_trades.json << 'EOF'
{
  "signals": [
    {
      "ticker": "SPY",
      "action": "BUY_CALL",
      "strike": 460.0,
      "expiration_days": 30,
      "confidence": 0.80,
      "reasoning": "Rate cuts coming, bullish trend"
    }
  ]
}
EOF
```

### Step 2: Push to GitHub
```bash
git add signals/my_trades.json
git commit -m "Add SPY call signal"
git push
```

### Step 3: Run the Bot
- Automatically runs every 3 hours via GitHub Actions
- Or trigger manually: GitHub → Actions → Trading Bot → Run workflow

---

## ⚠️ IMPORTANT NOTES

1. **Priority Order:** JSON signals > WhatsApp exports > Default test trades
2. **Confidence Threshold:** Bot only trades if confidence > 0.60
3. **Risk Management:** Max 2% portfolio risk per trade
4. **Claude Override:** Even with signals, Claude AI makes final decision
5. **Test Mode:** Set `FORCE_TEST_TRADE=true` to bypass signal requirements

---

## 📞 SUPPORT

- **Issues:** https://github.com/[your-username]/ai-options-trading-bot/issues
- **Logs:** Check GitHub Actions logs for processing details
- **Database:** Monitor Supabase for trade history