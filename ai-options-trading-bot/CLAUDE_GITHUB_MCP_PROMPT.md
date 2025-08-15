# 🤖 Claude GitHub MCP Integration Prompt

## For Claude with GitHub MCP Server Access

You have access to both WhatsApp messages and GitHub through MCP servers. Your task is to extract trading signals from WhatsApp and push them directly to the repository.

## Your Available MCP Tools

### GitHub MCP Tools You'll Use:
- `create_or_update_file` - To add signal JSON files
- `create_branch` - To create feature branches  
- `create_pull_request` - To submit PRs
- `push_files` - To push multiple files
- `get_file_contents` - To read existing signals

### Expected Workflow

```python
# 1. Extract WhatsApp signals (from your WhatsApp access)
signals = extract_whatsapp_signals("investChatIL", days=7)

# 2. Create branch via GitHub MCP
branch_name = f"signals-{datetime.now():%Y%m%d-%H%M%S}"
github.create_branch(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    branch=branch_name,
    from_branch="main"
)

# 3. Create signal file via GitHub MCP
filename = f"whatsapp_data/signals_{datetime.now():%Y%m%d_%H%M%S}.json"
github.create_or_update_file(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path=filename,
    content=json.dumps(signals, indent=2),
    message=f"signals: WhatsApp extract {datetime.now():%Y-%m-%d %H:%M}",
    branch=branch_name
)

# 4. Create PR via GitHub MCP
github.create_pull_request(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    title=f"📱 WhatsApp Signals: {datetime.now():%Y-%m-%d %H:%M}",
    body=pr_body,
    head=branch_name,
    base="main",
    labels=["whatsapp-signals", "auto-generated"]
)
```

## Signal JSON Structure Required

Create a file `whatsapp_data/signals_YYYYMMDD_HHMMSS.json`:

```json
{
  "metadata": {
    "source": "investChatIL",
    "extracted_at": "2024-08-15T10:30:00Z",
    "message_count": 150,
    "period_start": "2024-08-08T00:00:00Z",
    "period_end": "2024-08-15T10:30:00Z",
    "extractor": "Claude-GitHub-MCP",
    "version": "1.0"
  },
  "signals": [
    {
      "timestamp": "2024-08-15T09:30:00Z",
      "ticker": "NVDA",
      "action": "BUY_CALL",
      "strike": 850,
      "expiration_days": 30,
      "confidence": 0.85,
      "sentiment": "BULLISH",
      "urgency": "HIGH",
      "consensus_count": 3,
      "original_text": "נראה חזק, אני קונה קול 850",
      "translated_text": "Looks strong, I'm buying CALL 850",
      "supporting_messages": [
        {
          "timestamp": "2024-08-15T09:31:00Z",
          "text": "גם אני נכנס",
          "translation": "I'm in too"
        }
      ]
    }
  ],
  "market_summary": {
    "overall_sentiment": "BULLISH",
    "sentiment_score": 0.65,
    "top_mentioned_tickers": [
      {"ticker": "NVDA", "count": 12, "sentiment": "BULLISH"},
      {"ticker": "SPY", "count": 8, "sentiment": "BULLISH"},
      {"ticker": "AAPL", "count": 5, "sentiment": "BEARISH"}
    ],
    "key_themes": [
      "Tech earnings optimism",
      "Concern about interest rates",
      "Options expiry Friday positioning"
    ],
    "group_activity": {
      "messages_per_hour": 12.5,
      "active_members": 15,
      "response_time_avg_minutes": 3.2
    }
  },
  "high_confidence_trades": [
    {
      "ticker": "NVDA",
      "action": "BUY_CALL", 
      "strike": 850,
      "confidence": 0.85,
      "reason": "Strong group consensus (3+ members), specific strike mentioned"
    }
  ],
  "extraction_stats": {
    "processing_time_seconds": 2.4,
    "messages_analyzed": 150,
    "signals_extracted": 12,
    "high_confidence_count": 3,
    "hebrew_messages_translated": 45
  }
}
```

## PR Body Template

When creating the PR, use this body:

```markdown
## 📱 WhatsApp Trading Signals - Auto-Extracted

### 📊 Extraction Summary
- **Source**: investChatIL WhatsApp Group
- **Period**: {start_date} to {end_date}
- **Messages Analyzed**: {message_count}
- **High Confidence Signals**: {high_conf_count}
- **Extraction Method**: Claude + GitHub MCP

### 🎯 Top Trading Opportunities

| Ticker | Action | Strike | Expiry | Confidence | Consensus |
|--------|--------|--------|--------|------------|-----------|
{signals_table}

### 📈 Market Sentiment Analysis
- **Overall Sentiment**: {sentiment} ({score}/1.0)
- **Most Discussed**: {top_tickers}
- **Group Activity**: {activity_level}

### 🤖 Auto-Execution Candidates
These signals meet the confidence threshold (≥0.75) for automatic execution:

{auto_execute_list}

### 📋 Key Themes Detected
{themes_list}

### 🔄 Processing Details
- Extracted by: Claude via GitHub MCP
- Processing Time: {process_time}s
- Hebrew Translations: {hebrew_count}
- Next Extraction: {next_run}

---
*🤖 Auto-generated via Claude + GitHub MCP Integration*
*✅ This PR will be auto-processed by GitHub Actions*
```

## Step-by-Step Instructions for Claude

### 1. Read WhatsApp Messages
```
Use your WhatsApp access to read the last 7 days from investChatIL group
Focus on messages containing: tickers, CALL/PUT, קול/פוט, price levels
```

### 2. Extract and Analyze
```
- Identify stock tickers (AAPL, SPY, NVDA, etc.)
- Detect options signals (CALL/PUT with strikes)
- Translate Hebrew: קול→CALL, פוט→PUT, קנה→BUY, מכר→SELL
- Score confidence based on consensus and specificity
- Group similar signals within 5-minute windows
```

### 3. Create Branch via GitHub MCP
```python
github.create_branch(
    owner="liorsolomon",
    repo="ai-options-trading-bot", 
    branch=f"signals-{timestamp}",
    from_branch="main"
)
```

### 4. Push Signal File via GitHub MCP
```python
github.create_or_update_file(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path=f"whatsapp_data/signals_{timestamp}.json",
    content=json_content,
    message="signals: WhatsApp extract via Claude MCP",
    branch=branch_name
)
```

### 5. Create PR via GitHub MCP
```python
github.create_pull_request(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    title=f"📱 WhatsApp Signals: {date}",
    body=pr_body,
    head=branch_name,
    base="main",
    labels=["whatsapp-signals", "auto-generated", "claude-mcp"]
)
```

## Validation Checklist

Before creating the PR, ensure:
- [ ] At least 1 signal with confidence ≥ 0.75
- [ ] Valid JSON structure
- [ ] All timestamps in UTC
- [ ] Hebrew text includes English translation
- [ ] Tickers are valid US market symbols
- [ ] File path starts with `whatsapp_data/signals_`
- [ ] PR has "whatsapp-signals" label

## Expected GitHub Actions Response

Once you create the PR, GitHub Actions will:
1. Validate the JSON structure
2. Send high-confidence signals to trading bot
3. Execute approved trades on Alpaca
4. Comment results on the PR
5. Auto-merge if successful

## Success Metrics

Your extraction is successful when:
- ✅ PR created with green checks
- ✅ Bot comments "Signals validated"
- ✅ Trades show as "EXECUTED" or "SIMULATED"
- ✅ PR auto-merges within 5 minutes

## Error Handling

If the PR fails validation:
1. Check JSON syntax
2. Ensure confidence scores are 0.0-1.0
3. Verify timestamps are ISO format
4. Confirm file is in whatsapp_data/ directory

## Hebrew Translation Reference

Common terms to translate:
```
קול / קולים → CALL / CALLS
פוט / פוטים → PUT / PUTS
קנה / קניה / קונה → BUY / BUYING
מכר / מכירה / מוכר → SELL / SELLING
שורט → SHORT
לונג → LONG
עולה / עליה → UP / BULLISH
יורד / ירידה → DOWN / BEARISH
חזק → STRONG
חלש → WEAK
דחוף → URGENT
עכשיו → NOW
```

## Example GitHub MCP Commands

### Check if signals directory exists:
```python
github.get_file_contents(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path="whatsapp_data"
)
```

### Create the directory if needed:
```python
github.create_or_update_file(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path="whatsapp_data/.gitkeep",
    content="",
    message="Create whatsapp_data directory"
)
```

### Push signal file and create PR in one flow:
```python
# All via GitHub MCP tools
branch = f"signals-{datetime.now():%Y%m%d-%H%M%S}"
github.create_branch(...)
github.create_or_update_file(...)
github.create_pull_request(...)
```

---

## Ready to Execute?

1. Read WhatsApp messages from investChatIL
2. Extract and format signals as JSON
3. Use GitHub MCP to create branch
4. Push signal file via GitHub MCP
5. Create PR with proper labels
6. Watch as GitHub Actions processes everything automatically!

The entire process should take < 30 seconds and result in automated trades! 🚀