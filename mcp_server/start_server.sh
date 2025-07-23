#!/bin/bash

echo "🚀 Starting MCP Python-to-API Server..."
echo ""
echo "📍 Main server will run on: http://localhost:8000"
echo "📍 Generated APIs will run on: http://localhost:8001"
echo ""
echo "📝 Upload a Python file with:"
echo "   curl -F 'file=@your_script.py' http://localhost:8000/upload"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Start the server using the new startup script that properly manages processes
python start_mcp_server.py