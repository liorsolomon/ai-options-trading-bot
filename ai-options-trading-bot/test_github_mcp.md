# 🧪 Test GitHub MCP Connection

## Quick Test for Claude

Run this to verify your GitHub MCP is working:

### 1. Test Read Access
```python
# Try to read the README
github.get_file_contents(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path="README.md"
)
```

Expected: Should return the README content

### 2. Test Branch Creation
```python
# Create a test branch
github.create_branch(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    branch="test-mcp-connection",
    from_branch="main"
)
```

Expected: New branch created

### 3. Test File Creation
```python
# Create a test file
test_content = {
    "test": "GitHub MCP working",
    "timestamp": "2024-08-15T10:30:00Z",
    "created_by": "Claude"
}

github.create_or_update_file(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    path="test/mcp_test.json",
    content=json.dumps(test_content, indent=2),
    message="test: GitHub MCP connection",
    branch="test-mcp-connection"
)
```

Expected: File created in test branch

### 4. Test PR Creation
```python
# Create a test PR
github.create_pull_request(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    title="🧪 Test: GitHub MCP Connection",
    body="This is a test PR created by Claude via GitHub MCP.\n\nIf you see this, the connection is working!",
    head="test-mcp-connection",
    base="main",
    labels=["test"]
)
```

Expected: PR created successfully

## If All Tests Pass

You're ready to push real WhatsApp signals! Use the instructions in `CLAUDE_QUICK_PUSH.md`.

## If Tests Fail

Check:
1. Is the GitHub MCP server configured in your Claude settings?
2. Do you have write access to the repository?
3. Is the repository name correct: `liorsolomon/ai-options-trading-bot`?

## Clean Up After Testing

You can close the test PR without merging:
```python
# Optional: Close the test PR
github.close_pull_request(
    owner="liorsolomon",
    repo="ai-options-trading-bot",
    pull_number=PR_NUMBER
)
```