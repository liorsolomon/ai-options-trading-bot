# Setup Guide for AI Options Trading Bot

## Prerequisites

- Python 3.11+
- GitHub account
- PostgreSQL database (or Supabase/Neon account)

## Step 1: Alpaca Account Setup

1. **Create Alpaca Account**
   - Go to https://app.alpaca.markets/signup
   - Complete registration
   - Verify your email

2. **Enable Paper Trading**
   - Log into your Alpaca dashboard
   - Switch to "Paper Trading" mode (toggle in top-right)
   - This gives you $100,000 in virtual money

3. **Enable Options Trading**
   - Go to Account Settings
   - Request Options Trading approval
   - For paper trading, this is usually instant
   - You'll need Level 2 for most strategies

4. **Get API Keys**
   - Navigate to "API Keys" section
   - Generate new API keys for Paper Trading
   - Save both:
     - `ALPACA_API_KEY`
     - `ALPACA_SECRET_KEY`

## Step 2: GitHub Repository Setup

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/liorsolomon/ai-options-trading-bot.git
   cd ai-options-trading-bot
   ```

2. **Set Up GitHub Secrets**
   - Go to your repository on GitHub
   - Navigate to Settings → Secrets and variables → Actions
   - Add the following secrets:
     ```
     ALPACA_API_KEY=<your-alpaca-api-key>
     ALPACA_SECRET_KEY=<your-alpaca-secret-key>
     CLAUDE_API_KEY=<your-claude-api-key>
     DATABASE_URL=<your-database-url>
     ```

## Step 3: Database Setup

### Option A: Using Supabase (Recommended - Free Tier)

1. Create account at https://supabase.com
2. Create new project
3. Get connection string from Settings → Database
4. Your `DATABASE_URL` will look like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
   ```

### Option B: Using Neon (Alternative - Free Tier)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Your `DATABASE_URL` will be provided directly

## Step 4: Claude API Setup

1. **Get Claude API Key**
   - Go to https://console.anthropic.com
   - Create account or login
   - Generate API key
   - Add to GitHub Secrets as `CLAUDE_API_KEY`

## Step 5: Local Development Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Local Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_database.py
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

6. **Test Run Locally**
   ```bash
   python -m src.main
   ```

## Step 6: Activate GitHub Actions

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Enable workflows if prompted
4. The bot will now run automatically every 3 hours

## Step 7: Monitor Your Bot

1. **Check GitHub Actions**
   - Go to Actions tab to see run history
   - Download logs from each run

2. **Check Alpaca Dashboard**
   - Monitor your paper trading positions
   - View order history
   - Check P&L

3. **Database Monitoring**
   - Use Supabase/Neon dashboard to view data
   - Check signal history and performance

## Important Notes

- **Paper Trading Only**: Always use paper trading mode initially
- **API Rate Limits**: Be aware of rate limits for each service
- **Cost Management**: Monitor API usage to avoid unexpected charges
- **Risk Settings**: Review and adjust risk parameters in `config/strategies.yaml`

## Troubleshooting

### Common Issues

1. **"API key not valid" error**
   - Ensure you're using Paper Trading API keys
   - Check that keys are correctly set in GitHub Secrets

2. **"Options trading not enabled"**
   - Request options approval in Alpaca account settings
   - Wait for approval (usually instant for paper trading)

3. **Database connection errors**
   - Verify DATABASE_URL format
   - Check if database server is running
   - Ensure SSL mode is configured correctly

4. **GitHub Actions failing**
   - Check Actions logs for specific errors
   - Verify all secrets are set correctly
   - Ensure repository has Actions enabled

## Next Steps

1. Start with paper trading for at least 1 month
2. Monitor performance metrics
3. Adjust strategies based on results
4. Consider adding more data sources
5. Implement additional risk management features