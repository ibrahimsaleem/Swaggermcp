#!/usr/bin/env python3
"""
Test script for MCP bridge functionality.

This script simulates MCP client requests to test the bridge.
"""

import json
import subprocess
import time
import asyncio
import os
from pathlib import Path

async def test_mcp_bridge():
    """Test the MCP bridge with various requests."""
    print("🧪 Testing MCP Bridge\n")
    
    # Start the MCP bridge process
    process = await asyncio.create_subprocess_exec(
        'python', '-m', 'mcp_server.mcp_bridge',
        cwd=Path(__file__).parent,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={
            **os.environ,
            'MCP_SERVER_PORT': '8000',
            'GENERATED_API_PORT': '8001'
        }
    )
    
    async def send_request(method, params=None, request_id=1):
        """Send a request and get response."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id
        }
        if params:
            request["params"] = params
        
        print(f"→ Sending: {method}")
        process.stdin.write((json.dumps(request) + '\n').encode())
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode())
        print(f"← Response: {json.dumps(response, indent=2)}\n")
        return response
    
    try:
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Test 1: Initialize
        print("1. Testing initialization...")
        response = await send_request("initialize", {
            "protocolVersion": "1.0",
            "clientInfo": {
                "name": "test-client",
                "version": "1.0"
            }
        }, 1)
        
        # Test 2: List tools
        print("2. Testing tools/list...")
        response = await send_request("tools/list", {}, 2)
        
        # Test 3: Get server status
        print("3. Testing server status...")
        response = await send_request("tools/call", {
            "name": "get_server_status",
            "arguments": {}
        }, 3)
        
        # Test 4: Upload Python code
        print("4. Testing Python code upload...")
        test_code = """
def hello(name="world"):
    return f"Hello, {name}!"

def calculate(x, y, operation="add"):
    x, y = float(x), float(y)
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y if y != 0 else "Error: Division by zero"
"""
        
        response = await send_request("tools/call", {
            "name": "upload_python_file",
            "arguments": {
                "content": test_code
            }
        }, 4)
        
        # Wait for API to be ready
        await asyncio.sleep(2)
        
        # Test 5: List endpoints
        print("5. Testing endpoint listing...")
        response = await send_request("tools/call", {
            "name": "list_endpoints",
            "arguments": {}
        }, 5)
        
        # Test 6: Call an endpoint
        print("6. Testing endpoint call...")
        response = await send_request("tools/call", {
            "name": "call_endpoint",
            "arguments": {
                "endpoint": "/hello",
                "params": {"name": "MCP Test"}
            }
        }, 6)
        
        # Test 7: List resources
        print("7. Testing resources/list...")
        response = await send_request("resources/list", {}, 7)
        
        # Test 8: Read a resource
        print("8. Testing resources/read...")
        response = await send_request("resources/read", {
            "uri": "api://endpoints"
        }, 8)
        
        # Test 9: List prompts
        print("9. Testing prompts/list...")
        response = await send_request("prompts/list", {}, 9)
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        process.terminate()
        await process.wait()
        print("\n🧹 Cleaned up")

if __name__ == "__main__":
    import os
    asyncio.run(test_mcp_bridge())