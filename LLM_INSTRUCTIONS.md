# 🤖 Instructions for WhatsApp LLM

## Your Mission
Extract trading signals from WhatsApp group "investChatIL" and create a GitHub pull request that will trigger automated trading.

## Quick Steps

### 1. Extract Signals
```python
# Read last 7 days from investChatIL
messages = read_whatsapp_group("investChatIL", days=7)

# Extract trading signals
signals = extract_trading_signals(messages)

# Filter high confidence only
high_confidence = [s for s in signals if s.confidence >= 0.7]
```

### 2. Create JSON File
Save to: `whatsapp_data/signals_[YYYYMMDD_HHMMSS].json`

Required structure:
```json
{
  "metadata": {...},
  "signals": [...],
  "market_summary": {...},
  "high_confidence_trades": [...]
}
```

### 3. Create Pull Request
```bash
# Commands to run
git checkout -b whatsapp-signals-$(date +%Y%m%d-%H%M%S)
git add whatsapp_data/signals_*.json
git commit -m "signals: WhatsApp extract $(date)"
git push origin $(git branch --show-current)
gh pr create --title "📱 WhatsApp Signals: $(date)" --label "whatsapp-signals"
```

## Key Rules

### ✅ INCLUDE
- Stock tickers (AAPL, SPY, NVDA)
- Options terms (CALL/קול, PUT/פוט)
- Price targets and strikes
- Multiple member agreements
- Urgent/time-sensitive signals

### ❌ EXCLUDE  
- Questions without answers
- Past tense trades
- Non-US stocks
- General chat/greetings
- Unverifiable claims

### 🔤 Hebrew → English
- קול → CALL
- פוט → PUT
- קנה → BUY
- מכר → SELL
- דחוף → URGENT

## Confidence Scoring

| Confidence | Criteria | Action |
|------------|----------|--------|
| 0.9-1.0 | Multiple agrees + specific strike + urgent | AUTO-TRADE |
| 0.7-0.8 | Clear signal + ticker + direction | AUTO-TRADE |
| 0.5-0.6 | General sentiment | MONITOR |
| <0.5 | Vague | IGNORE |

## GitHub Integration

The PR will trigger:
1. **Validation** - JSON format check
2. **Claude Analysis** - AI evaluates each signal
3. **Risk Check** - Position sizing and limits
4. **Execution** - Trades placed on Alpaca
5. **Auto-merge** - PR merged if successful

## Example Output

Your PR should create this file:
```
whatsapp_data/signals_20240815_103000.json
```

With signals like:
```json
{
  "timestamp": "2024-08-15T09:30:00Z",
  "ticker": "NVDA",
  "action": "BUY_CALL",
  "strike": 850,
  "confidence": 0.85,
  "original_text": "NVDA קול 850 עכשיו!",
  "translated_text": "NVDA CALL 850 now!"
}
```

## Success Metrics

Your extraction is successful if:
- ✅ At least 1 signal with confidence ≥ 0.75
- ✅ Valid JSON format
- ✅ PR created with "whatsapp-signals" label
- ✅ GitHub Actions shows green check
- ✅ Bot comments with execution results

## Remember

- **Privacy**: Anonymize senders (Member_abc123)
- **Time**: Use UTC timestamps
- **Accuracy**: Better to miss signals than create false ones
- **Context**: Include surrounding messages for clarity

## Need the Full Prompt?
See `WHATSAPP_LLM_PROMPT.md` for complete details.

---

**Ready? Extract signals → Create JSON → Submit PR → Watch trades execute! 🚀**