# AI Options Trading Bot

An automated options trading bot powered by Claude Code, running on GitHub Actions with paper trading via Alpaca Markets.

## Features

- **AI-Driven Decisions**: Uses Claude Code for market analysis and trading decisions
- **Automated Execution**: Runs every 3 hours via GitHub Actions
- **Options Focus**: Specializes in PUT/CALL options strategies
- **Paper Trading**: Safe simulation mode using Alpaca Markets
- **Historical Learning**: Maintains database of successful signal patterns
- **Multi-Source Data**: Integrates multiple market data providers

## Architecture

The system consists of:
- Decision engine powered by Claude Code
- Data pipeline for market information
- Trading execution via Alpaca API
- GitHub Actions for automation
- PostgreSQL for historical data

## Setup

1. Clone the repository
2. Set up GitHub Secrets (see Configuration section)
3. Configure Alpaca paper trading account
4. Initialize database
5. Deploy GitHub Actions workflow

## Configuration

Required GitHub Secrets:
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_SECRET_KEY`: Your Alpaca secret key
- `CLAUDE_API_KEY`: Claude API key
- `DATABASE_URL`: PostgreSQL connection string
- `NEWS_API_KEY`: NewsAPI key (optional)

## Project Structure

```
ai-options-trading-bot/
├── .github/workflows/    # GitHub Actions workflows
├── src/                  # Source code
│   ├── claude_integration/
│   ├── data_sources/
│   ├── strategies/
│   ├── signals/
│   ├── execution/
│   └── database/
├── config/              # Configuration files
├── scripts/             # Utility scripts
├── tests/              # Test suite
└── docker/             # Container configuration
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run backtesting
python scripts/backtest.py

# Analyze performance
python scripts/analyze_performance.py
```

## Risk Management

- Paper trading only (simulation mode)
- Position size limits enforced
- Maximum daily loss protection
- Diversification requirements
- Automated stop-loss mechanisms

## License

MIT