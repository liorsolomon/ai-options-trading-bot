# Cloud Database Setup - REQUIRED for GitHub Actions

**IMPORTANT**: GitHub Actions containers are ephemeral. Local SQLite won't work - you MUST use a cloud database!

## Option 1: Supabase (Recommended - Free Tier)

### Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Sign up with GitHub (recommended) or email
3. Click "New project"

### Step 2: Create Project
1. **Project name**: `trading-bot-db`
2. **Database Password**: Generate a strong password (SAVE THIS!)
3. **Region**: Choose closest to you
4. Click "Create new project" (takes ~2 minutes)

### Step 3: Get Connection String
1. Go to Settings → Database
2. Find "Connection string" section
3. Select "URI" tab
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual password

Your connection string will look like:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
```

### Step 4: Add to GitHub Secrets
```bash
gh secret set DATABASE_URL --body "postgresql://postgres:YOUR-PASSWORD@db.xxxxxxxxxxxx.supabase.co:5432/postgres"
```

## Option 2: Neon (Alternative - Free Tier)

### Step 1: Create Neon Account
1. Go to https://neon.tech
2. Sign up with GitHub or email
3. Click "Create a project"

### Step 2: Create Database
1. **Project name**: `trading-bot`
2. **Database name**: `trading_bot_db`
3. **Region**: Choose closest
4. Click "Create project"

### Step 3: Get Connection String
1. Dashboard shows connection string immediately
2. Copy the full connection string

It will look like:
```
postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/trading_bot_db
```

### Step 4: Add to GitHub Secrets
```bash
gh secret set DATABASE_URL --body "YOUR-NEON-CONNECTION-STRING"
```

## Option 3: Aiven (Free Trial - 1 Month)

### Step 1: Create Aiven Account
1. Go to https://aiven.io
2. Sign up for free trial
3. Choose PostgreSQL

### Step 2: Create Service
1. **Cloud**: Any (AWS/GCP/Azure)
2. **Region**: Closest to you
3. **Plan**: Free trial
4. **Service name**: `trading-bot-db`

### Step 3: Get Connection String
1. Go to service overview
2. Copy "Service URI"

## Initialize Your Cloud Database

After setting up your cloud database:

### 1. Update Local .env
```bash
# Edit .env file with your cloud DATABASE_URL
DATABASE_URL=postgresql://...your-cloud-url...
```

### 2. Initialize Tables
```bash
source venv/bin/activate
python scripts/init_database.py
```

### 3. Verify Connection
```bash
python scripts/init_database.py --test
```

## Verify GitHub Actions Setup

### Test GitHub Secret
```bash
gh secret list
# Should show DATABASE_URL in the list
```

### Trigger a Test Run
```bash
gh workflow run trading-bot.yml
```

### Check Logs
```bash
gh run list --workflow=trading-bot.yml
gh run view  # Select the latest run
```

## Important Notes

1. **Free Tier Limits**:
   - Supabase: 500MB storage, 2GB bandwidth/month
   - Neon: 3GB storage, unlimited compute (with autosuspend)
   - Both are sufficient for paper trading

2. **Security**:
   - Never commit DATABASE_URL to git
   - Always use GitHub Secrets for production
   - Rotate passwords regularly

3. **Backups**:
   - Supabase: Automatic daily backups (7 days retention on free)
   - Neon: Point-in-time recovery
   - Consider exporting important data periodically

4. **Monitoring**:
   - Both services provide dashboards
   - Monitor storage usage
   - Set up alerts for quota limits

## Troubleshooting

### "Connection refused" Error
- Check if database is active (may auto-pause on free tier)
- Verify connection string format
- Ensure SSL mode is correct

### "Database does not exist"
- Some providers require creating database first
- Use provider's dashboard to create database
- Update connection string with correct database name

### GitHub Actions Failing
- Check GitHub Secrets are set correctly
- Verify DATABASE_URL format
- Check Actions logs for specific errors

## Data Persistence Benefits

With cloud database:
- ✅ Data persists between GitHub Actions runs
- ✅ Access data from multiple environments
- ✅ Built-in backups and recovery
- ✅ Real-time monitoring dashboards
- ✅ Can query historical data anytime
- ✅ Share data between local and cloud environments