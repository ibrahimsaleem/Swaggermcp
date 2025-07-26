# MCP Bridge Fix

## Problem
The original `mcp_bridge.py` was incorrectly starting a new uvicorn subprocess for the orchestrator on every new JSON-RPC session/init request rather than only once at startup. This led to repeated bind errors (`address already in use`) because the port was already bound by a previous instance.

## Solution
The fix involves:

1. **Modified `mcp_bridge.py`**: Removed the subprocess spawning logic from `run_mcp_server()` function. The MCP bridge now expects the FastAPI server to be started separately.

2. **Created `start_mcp_server.py`**: A new startup script that properly manages both the FastAPI server and MCP bridge processes to avoid port binding conflicts.

3. **Updated startup scripts**: Modified `start_server.sh` and `Dockerfile` to use the new startup approach.

## Architecture
```
start_mcp_server.py (main orchestrator)
├── FastAPI Server (port 8000) - started once
└── MCP Bridge (stdin/stdout) - handles JSON-RPC requests
    └── Generated API Server (port 8001) - managed by APIServerRunner
```

## Usage

### Option 1: Using the new startup script (Recommended)
```bash
cd mcp_server
python start_mcp_server.py
```

### Option 2: Using the shell script
```bash
cd mcp_server
chmod +x start_server.sh
./start_server.sh
```

### Option 3: Using Docker
```bash
cd mcp_server
docker build -t mcp-server .
docker run -p 8000:8000 -p 8001:8001 mcp-server
```

## Testing the Fix
Run the test script to verify the fix works:
```bash
cd mcp_server
python test_fix.py
```

This will test:
- Basic MCP bridge functionality
- Multiple session handling without port binding issues
- FastAPI server startup and status

## Key Changes

### mcp_bridge.py
- Removed subprocess spawning from `run_mcp_server()`
- Added logging to indicate expected FastAPI server location
- Simplified cleanup process

### start_mcp_server.py (New)
- Manages FastAPI server startup once
- Handles signal interrupts gracefully
- Proper process cleanup on shutdown

### start_server.sh
- Updated to use the new startup script
- Maintains backward compatibility

### Dockerfile
- Updated CMD to use the new startup script
- Ensures proper process management in containerized environment

## Benefits
1. **No more port binding conflicts**: FastAPI server starts only once
2. **Proper process management**: Clean startup and shutdown
3. **Better error handling**: Graceful handling of interrupts and failures
4. **Maintains functionality**: All original MCP bridge features preserved
5. **Docker compatibility**: Works correctly in containerized environments

## Troubleshooting
If you encounter issues:

1. **Port already in use**: Make sure no other instances are running
   ```bash
   lsof -i :8000
   lsof -i :8001
   ```

2. **Permission denied**: Ensure scripts are executable
   ```bash
   chmod +x start_server.sh
   chmod +x start_mcp_server.py
   ```

3. **Dependencies missing**: Install requirements
   ```bash
   pip install -r requirements.txt
   ```