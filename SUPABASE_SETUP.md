# 🚀 Supabase Database Setup - Step by Step

Follow these steps to set up your FREE cloud database that will persist all your trading data.

## Step 1: Create Supabase Account

1. **Open Supabase**: https://supabase.com
2. Click **"Start your project"** (green button)
3. Sign up with:
   - GitHub (recommended - one click)
   - OR email/password
4. Verify your email if needed

## Step 2: Create Your Database Project

Once logged in:

1. Click **"New project"**
2. Fill in:
   - **Organization**: Select or create one
   - **Project name**: `trading-bot-db`
   - **Database Password**: 
     - Click "Generate a password"
     - **COPY AND SAVE THIS PASSWORD!** You'll need it
   - **Region**: Choose closest to you (e.g., US East, EU Central)
3. Click **"Create new project"**
4. Wait ~2 minutes for setup (you'll see a loading screen)

## Step 3: Get Your Connection String

Once your project is ready:

1. Click **Settings** (gear icon in sidebar)
2. Click **Database** (in settings menu)
3. Scroll to **"Connection string"** section
4. Select **"URI"** tab
5. You'll see:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. **Copy this entire string**
7. Replace `[YOUR-PASSWORD]` with your actual password from Step 2

Your final connection string should look like:
```
postgresql://postgres:YourActualPassword123@db.abcdefghijk.supabase.co:5432/postgres
```

## Step 4: Add to GitHub Secrets

### Option A: Using GitHub CLI (easiest)
```bash
gh secret set DATABASE_URL --body "postgresql://postgres:YourPassword@db.xxxx.supabase.co:5432/postgres"
```

### Option B: GitHub Web Interface
1. Go to: https://github.com/liorsolomon/ai-options-trading-bot/settings/secrets/actions
2. Click **"New repository secret"**
3. Add:
   - **Name**: `DATABASE_URL`
   - **Value**: Your connection string from Step 3
4. Click **"Add secret"**

## Step 5: Update Local .env File

Edit your `.env` file:
```bash
DATABASE_URL=postgresql://postgres:YourPassword@db.xxxx.supabase.co:5432/postgres
```

## Step 6: Initialize Database Tables

```bash
# Activate virtual environment
source venv/bin/activate

# Install any missing packages
pip install psycopg2-binary sqlalchemy asyncpg

# Initialize database
python scripts/init_database.py
```

You should see:
```
✅ Database tables created successfully!
Created 7 tables:
  - signals
  - trades
  - position_updates
  - market_snapshots
  - strategy_performance
  - decision_logs
  - alerts
```

## Step 7: Verify Everything Works

Test the connection:
```bash
python scripts/init_database.py --test
```

## ✅ You're Done!

Your database is now set up with:
- **Persistent storage** across all GitHub Actions runs
- **500MB free storage** (enough for years of trading data)
- **Automatic daily backups**
- **Real-time dashboard** at app.supabase.com

## 📊 Monitor Your Database

1. Go to https://app.supabase.com
2. Click on your project
3. Use **Table Editor** to view your data
4. Check **Database** → **Statistics** for usage

## 🎯 Next Steps

1. The bot will now automatically use this database
2. GitHub Actions will persist all trading data
3. You can query historical signals and performance
4. Access your data from anywhere

## Need Help?

If you get stuck at any step:
1. Make sure you saved your database password
2. Check that the connection string format is correct
3. Ensure you replaced `[YOUR-PASSWORD]` with your actual password
4. Try the test connection script to debug issues