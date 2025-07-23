#!/usr/bin/env python3
"""
Startup script for the MCP server that properly manages the FastAPI server
and MCP bridge to avoid port binding conflicts.

This script starts the FastAPI server once and then runs the MCP bridge.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_fastapi_server(port: str = "8000"):
    """Start the FastAPI server in the background."""
    print(f"Starting FastAPI server on port {port}...")
    
    # Start the FastAPI server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", port],
        cwd=Path(__file__).parent
    )
    
    # Give it time to start
    time.sleep(3)
    
    # Check if it started successfully
    if server_process.poll() is not None:
        print("Failed to start FastAPI server")
        return None
    
    print("FastAPI server started successfully")
    return server_process

def run_mcp_bridge():
    """Run the MCP bridge."""
    print("Starting MCP Bridge...")
    
    # Run the MCP bridge
    bridge_process = subprocess.Popen(
        [sys.executable, "mcp_bridge.py"],
        cwd=Path(__file__).parent,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    return bridge_process

def main():
    """Main startup function."""
    # Get ports from environment or use defaults
    server_port = os.getenv("MCP_SERVER_PORT", "8000")
    
    # Start the FastAPI server
    server_process = start_fastapi_server(server_port)
    if server_process is None:
        sys.exit(1)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\nShutting down...")
        if server_process:
            server_process.terminate()
            server_process.wait()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the MCP bridge
        bridge_process = run_mcp_bridge()
        
        # Wait for the bridge to finish
        bridge_process.wait()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    finally:
        # Clean up
        print("Cleaning up...")
        if server_process:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()