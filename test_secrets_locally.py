#!/usr/bin/env python3
"""
Demonstrate GitHub Secrets security model - what can and cannot be accessed locally
"""

import os
import subprocess
import json

print("=" * 80)
print("GITHUB SECRETS SECURITY DEMONSTRATION")
print("=" * 80)

# 1. Check what GitHub CLI can show us
print("\n1. CHECKING GITHUB SECRETS WITH CLI")
print("-" * 40)

try:
    # List all secrets (names only, not values)
    result = subprocess.run(
        ["gh", "secret", "list", "--repo", "liorsolomon/ai-options-trading-bot"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Secrets found in repository:")
        print(result.stdout)
    else:
        print("❌ Could not list secrets:", result.stderr)
except Exception as e:
    print(f"❌ GitHub CLI error: {e}")

# 2. Try to get ANTHROPIC_API_KEY info (NOT the value)
print("\n2. CHECKING ANTHROPIC_API_KEY METADATA")
print("-" * 40)

try:
    api_result = subprocess.run(
        ["gh", "api", "repos/liorsolomon/ai-options-trading-bot/actions/secrets/ANTHROPIC_API_KEY"],
        capture_output=True,
        text=True
    )
    
    if api_result.returncode == 0:
        secret_info = json.loads(api_result.stdout)
        print("✅ ANTHROPIC_API_KEY exists in GitHub secrets")
        print(f"   Created: {secret_info.get('created_at')}")
        print(f"   Updated: {secret_info.get('updated_at')}")
    else:
        print("❌ ANTHROPIC_API_KEY not found in GitHub secrets")
except Exception as e:
    print(f"❌ Could not check secret: {e}")

# 3. Show what IS available locally
print("\n3. LOCAL ENVIRONMENT VARIABLES")
print("-" * 40)

local_keys = [
    "ANTHROPIC_API_KEY",
    "CLAUDE_API_KEY",
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
    "DATABASE_URL"
]

for key in local_keys:
    value = os.getenv(key)
    if value:
        # Show only partial value for security
        masked = f"{value[:7]}...{value[-4:]}" if len(value) > 15 else "***"
        print(f"✅ {key}: {masked}")
    else:
        print(f"❌ {key}: Not set locally")

# 4. Explain the security model
print("\n4. GITHUB SECRETS SECURITY MODEL")
print("-" * 40)
print("""
🔒 KEY FACTS:
1. GitHub Secrets are ENCRYPTED at rest
2. They can ONLY be accessed within GitHub Actions workflows
3. The GitHub CLI and API can show that a secret EXISTS
4. The actual VALUES are never exposed outside of workflows
5. This is by design for security - secrets cannot leak

📝 TO USE SECRETS LOCALLY:
1. Go to: https://github.com/liorsolomon/ai-options-trading-bot/settings/secrets/actions
2. Click on ANTHROPIC_API_KEY
3. Copy the value manually (you must be the repo owner)
4. Set it locally:
   export ANTHROPIC_API_KEY='your-key-here'
   export CLAUDE_API_KEY='your-key-here'  # Same value

🔧 ALTERNATIVELY, CREATE A .env FILE:
   echo "ANTHROPIC_API_KEY=your-key-here" >> .env
   echo "CLAUDE_API_KEY=your-key-here" >> .env
""")

# 5. Create a workflow to verify the secret works
print("\n5. VERIFYING SECRET IN GITHUB ACTIONS")
print("-" * 40)
print("I've already created .github/workflows/test-secrets.yml")
print("This workflow CAN access the secret value when run in GitHub Actions")
print("\nTo test it:")
print("1. Push this code: git push")
print("2. Go to Actions tab on GitHub")
print("3. Run 'Test Secrets' workflow manually")
print("4. It will show if ANTHROPIC_API_KEY is set correctly")

print("\n" + "=" * 80)
print("SUMMARY: GitHub Secrets are secure and cannot be retrieved locally.")
print("You must copy them manually from GitHub web interface.")
print("=" * 80)