#!/bin/bash
# Test WhatsApp MCP Server Connection

echo "🔌 Testing WhatsApp MCP Server Connection"
echo "=========================================="

# Test if uv command exists
if ! command -v /opt/homebrew/bin/uv &> /dev/null; then
    echo "❌ uv command not found at /opt/homebrew/bin/uv"
    echo "   Install with: brew install uv"
    exit 1
fi

echo "✅ Found uv command"

# Check if MCP server directory exists
MCP_DIR="/Users/liorsolomon/mcp-servers/whatsapp-mcp/whatsapp-mcp-server"
if [ ! -d "$MCP_DIR" ]; then
    echo "❌ MCP server directory not found: $MCP_DIR"
    echo "   You may need to clone/install the WhatsApp MCP server"
    exit 1
fi

echo "✅ Found MCP server directory"

# Try to run a simple test
echo ""
echo "📡 Attempting to connect to WhatsApp MCP server..."
echo "   Command: /opt/homebrew/bin/uv --directory $MCP_DIR run main.py"

# Create a simple MCP request to test
TEST_REQUEST='{"jsonrpc":"2.0","method":"list_tools","id":1}'

# Try to call the server
echo "$TEST_REQUEST" | /opt/homebrew/bin/uv --directory "$MCP_DIR" run main.py 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ MCP server responded successfully!"
    echo ""
    echo "🎯 To fetch WhatsApp data:"
    echo "   python scripts/fetch_whatsapp_mcp.py"
else
    echo ""
    echo "⚠️  MCP server didn't respond as expected"
    echo ""
    echo "💡 Try manual export instead:"
    echo "   1. Export chat from WhatsApp"
    echo "   2. Run: ./scripts/quick_upload.sh"
fi