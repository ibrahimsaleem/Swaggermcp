#!/usr/bin/env python3
"""
Test script for MCP server functionality.

This script:
1. Starts the MCP server
2. Uploads a test Python file
3. Tests the generated endpoints
4. Displays results
"""

import time
import requests
import subprocess
import sys
import json
from pathlib import Path

def test_mcp_server():
    print("🚀 Starting MCP Server Test Suite\n")
    
    # Start the MCP server
    print("1. Starting MCP server on port 8000...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=Path(__file__).parent
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Check server status
        print("2. Checking server status...")
        status_resp = requests.get("http://localhost:8000/status")
        print(f"   Status: {status_resp.json()}\n")
        
        # Upload test file
        print("3. Uploading test_funcs.py...")
        with open("test_funcs.py", "rb") as f:
            files = {"file": ("test_funcs.py", f, "text/x-python")}
            upload_resp = requests.post("http://localhost:8000/upload", files=files)
        
        result = upload_resp.json()
        print(f"   Upload response: {json.dumps(result, indent=2)}\n")
        
        # Wait for generated server to start
        time.sleep(2)
        
        # Test generated endpoints
        print("4. Testing generated endpoints...")
        base_url = "http://localhost:8001"
        
        tests = [
            ("GET", f"{base_url}/add?x=5&y=3", "Add 5 + 3"),
            ("GET", f"{base_url}/multiply?a=4&b=2.5", "Multiply 4 * 2.5"),
            ("GET", f"{base_url}/greet?name=MCP&greeting=Welcome", "Greet with custom message"),
            ("GET", f"{base_url}/parse_text?text=  hello world  &uppercase=true", "Parse text with uppercase"),
            ("GET", f"{base_url}/calculate_area?shape=square&width=5", "Calculate square area"),
        ]
        
        for method, url, desc in tests:
            print(f"\n   Testing: {desc}")
            print(f"   URL: {url}")
            resp = requests.request(method, url)
            print(f"   Result: {resp.json()}")
        
        print(f"\n5. ✅ All tests completed!")
        print(f"\n📚 Swagger UI available at: {result['swagger_url']}")
        print(f"📋 OpenAPI spec at: {result['openapi_url']}")
        
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        server_proc.terminate()
        server_proc.wait()
        print("   Server stopped.")

if __name__ == "__main__":
    test_mcp_server()