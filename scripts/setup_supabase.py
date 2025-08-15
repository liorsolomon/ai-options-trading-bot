#!/usr/bin/env python3
"""
Quick setup guide for Supabase database
"""

import webbrowser
import time


def setup_supabase():
    """Interactive Supabase setup guide"""
    
    print("=" * 60)
    print("🚀 SUPABASE DATABASE SETUP")
    print("=" * 60)
    print("\nThis will guide you through setting up a FREE cloud database.")
    print("Your data will persist between GitHub Actions runs!\n")
    
    input("Press Enter to open Supabase in your browser...")
    webbrowser.open("https://supabase.com")
    
    print("\n📝 STEP 1: Create Account")
    print("-" * 40)
    print("1. Click 'Start your project'")
    print("2. Sign up with GitHub (recommended) or email")
    print("3. Verify your email if needed")
    input("\nPress Enter when done...")
    
    print("\n📝 STEP 2: Create Project")
    print("-" * 40)
    print("1. Click 'New project'")
    print("2. Project name: 'trading-bot-db'")
    print("3. Database Password: Generate a strong one")
    print("4. IMPORTANT: Copy and save your password!")
    print("5. Region: Choose closest to you")
    print("6. Click 'Create new project'")
    print("\n⏳ This takes about 2 minutes...")
    input("\nPress Enter when your project is ready...")
    
    print("\n📝 STEP 3: Get Connection String")
    print("-" * 40)
    print("1. Go to Settings (gear icon) → Database")
    print("2. Find 'Connection string' section")
    print("3. Select 'URI' tab")
    print("4. You'll see something like:")
    print("\n   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres")
    print("\n5. Copy this string")
    
    connection_string = input("\nPaste your connection string here: ").strip()
    
    if "[YOUR-PASSWORD]" in connection_string:
        password = input("Enter your database password: ").strip()
        connection_string = connection_string.replace("[YOUR-PASSWORD]", password)
    
    print("\n📝 STEP 4: Add to GitHub Secrets")
    print("-" * 40)
    print("Run this command in your terminal:\n")
    print(f'gh secret set DATABASE_URL --body "{connection_string}"')
    print("\nOr manually:")
    print("1. Go to your GitHub repo")
    print("2. Settings → Secrets and variables → Actions")
    print("3. New repository secret")
    print("4. Name: DATABASE_URL")
    print(f"5. Value: {connection_string}")
    
    print("\n📝 STEP 5: Update Local .env")
    print("-" * 40)
    
    update_local = input("\nUpdate local .env file? (y/n): ").lower()
    if update_local == 'y':
        try:
            with open(".env", "r") as f:
                lines = f.readlines()
            
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("DATABASE_URL="):
                    lines[i] = f'DATABASE_URL={connection_string}\n'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'\nDATABASE_URL={connection_string}\n')
            
            with open(".env", "w") as f:
                f.writelines(lines)
            
            print("✅ Updated .env file")
        except Exception as e:
            print(f"❌ Could not update .env: {e}")
            print(f"\nManually add to .env:")
            print(f"DATABASE_URL={connection_string}")
    
    print("\n📝 STEP 6: Initialize Database")
    print("-" * 40)
    print("Run these commands:\n")
    print("source venv/bin/activate")
    print("python scripts/init_database.py")
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nYour Supabase database is ready for:")
    print("• Persistent storage across GitHub Actions runs")
    print("• Historical signal tracking")
    print("• Performance analytics")
    print("• Real-time monitoring")
    print("\nFree tier includes:")
    print("• 500MB storage")
    print("• 2GB bandwidth/month")
    print("• Automatic daily backups")
    print("• Dashboard for monitoring")
    
    print("\n🎯 Next Steps:")
    print("1. Initialize the database tables")
    print("2. Test GitHub Actions workflow")
    print("3. Monitor your first trades!")


if __name__ == "__main__":
    setup_supabase()