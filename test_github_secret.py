#!/usr/bin/env python3
"""
Test GitHub secret access - Note: This CANNOT retrieve actual secret values
GitHub secrets are encrypted and only accessible within GitHub Actions
"""

import subprocess
import json

# This can only show that the secret EXISTS, not its value
result = subprocess.run(
    ["gh", "secret", "list", "--repo", "liorsolomon/ai-options-trading-bot"],
    capture_output=True,
    text=True
)

print("GitHub Secrets in repository:")
print(result.stdout)

# Try to get secret via API - this will NOT return the actual value
api_result = subprocess.run(
    ["gh", "api", "repos/liorsolomon/ai-options-trading-bot/actions/secrets/ANTHROPIC_API_KEY"],
    capture_output=True,
    text=True
)

if api_result.returncode == 0:
    secret_info = json.loads(api_result.stdout)
    print("\nANTHROPIC_API_KEY secret info:")
    print(f"  Name: {secret_info.get('name')}")
    print(f"  Created: {secret_info.get('created_at')}")
    print(f"  Updated: {secret_info.get('updated_at')}")
    print("\n⚠️  NOTE: The actual secret value CANNOT be retrieved via API or CLI")
    print("    Secrets can only be accessed within GitHub Actions workflows")
else:
    print(f"\nError accessing secret info: {api_result.stderr}")

print("\n📝 To use the secret locally, you need to:")
print("1. Go to GitHub.com > Settings > Secrets > ANTHROPIC_API_KEY")
print("2. Copy the value manually")
print("3. Set it as a local environment variable:")
print("   export ANTHROPIC_API_KEY='your-key-here'")