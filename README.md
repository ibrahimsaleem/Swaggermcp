# Swaggermcp

---

# MCP Python-to-API Generator (MVP)

Upload any Python script with top-level functions. The orchestrator parses the functions and exposes each as a FastAPI endpoint with auto-generated Swagger docs.

## Quick Start

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start the MCP server
uvicorn main:app --reload --port 8000
```

## Usage

### Upload a Python script

```bash
curl -F "file=@examples/sample_funcs.py" http://localhost:8000/upload
```

### Response

```json
{
  "message": "Endpoints created.",
  "swagger_url": "http://localhost:8001/docs",
  "openapi_url": "http://localhost:8001/openapi.json",
  "endpoints": ["/add", "/subtract"]
}
```

Open the Swagger URL in a browser to test your functions.

## How It Works

1. `/upload` accepts `.py` files
2. We AST-parse top-level `def` functions
3. Generate `generated_fastapi_app.py`
4. Restart a uvicorn subprocess serving those endpoints
5. Reply with test URLs

## Example Test File

Create `test_funcs.py`:
```python
def add(x, y):
    """Add two numbers."""
    return int(x) + int(y)

def greet(name="world"):
    """Greet someone."""
    return f"Hello, {name}!"

def multiply(a, b):
    """Multiply two numbers."""
    return float(a) * float(b)
```

Upload it:
```bash
curl -F "file=@test_funcs.py" http://localhost:8000/upload
```

Then visit http://localhost:8001/docs to see and test your endpoints.

## Limitations (MVP)

- Query params only; all strings coerced at runtime
- No nested imports resolution
- No security / sandboxing
- Single upload at a time (latest wins)
- No async function support yet

## Security Warning

⚠️ **Never execute untrusted user Python code directly on a production host.**

For MVP/dev: OK. For real use, isolate via containers, firejail, gVisor, or serverless workers.

## Architecture

- **main.py**: MCP orchestration server that handles file uploads
- **utils/code_parser.py**: AST-based function extraction
- **utils/fastapi_writer.py**: Generates FastAPI code from parsed functions
- **utils/runner.py**: Manages uvicorn subprocess lifecycle
- **generated_fastapi_app.py**: Auto-generated API (overwritten on each upload)

## Type Handling

- All function params assumed `str` inputs (safer + predictable from query params)
- Runtime type coercion attempts: int → float → bool → JSON → string
- Return values serialized to JSON (best-effort)

## Roadmap

- Type hints → Pydantic models
- POST for complex JSON bodies
- Auth / sandboxing
- Multi-file module support
- Versioned APIs
- Async function support

## MCP Integration Pattern

In Cursor IDE (or any MCP client), you'd:
1. Detect file save → call `/upload`
2. Show returned Swagger URL to user
3. Optionally fetch `/openapi.json` and surface endpoint palette

## Connecting MCP Clients

This server now includes full MCP (Model Context Protocol) support! See [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) for detailed instructions on connecting:

- **Claude Desktop**: Add to `claude_desktop_config.json`
- **Cursor IDE**: Configure in `.cursor/mcp_config.json`
- **MCP CLI**: Use `mcp connect` command
- **Custom Clients**: Connect via stdin/stdout JSON-RPC

### Quick Setup for Claude Desktop

```json
{
  "mcpServers": {
    "python-to-api": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_bridge"],
      "cwd": "/absolute/path/to/mcp_server"
    }
  }
}
```

The MCP bridge (`mcp_bridge.py`) provides tools for:
- Uploading Python files
- Listing generated endpoints
- Calling API endpoints
- Checking server status

---

# MCP Client Connection Guide

This guide explains how to connect various MCP (Model Context Protocol) clients to the Python-to-API MCP server.

## Overview

The Python-to-API MCP server implements the Model Context Protocol, allowing AI assistants like Claude to:
- Upload Python files and convert functions to REST APIs
- Query available endpoints
- Execute API calls
- Access Swagger documentation

## Connection Methods

### 1. Claude Desktop App

Add this server to your Claude Desktop configuration:

1. Open Claude Desktop settings
2. Navigate to "Developer" → "MCP Servers"
3. Add the following configuration:

```json
{
  "python-to-api": {
    "command": "python",
    "args": ["-m", "mcp_server.mcp_bridge"],
    "cwd": "/path/to/mcp_server",
    "env": {
      "MCP_SERVER_PORT": "8000",
      "GENERATED_API_PORT": "8001"
    }
  }
}
```

Or edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "python-to-api": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_bridge"],
      "cwd": "/absolute/path/to/mcp_server",
      "env": {
        "MCP_SERVER_PORT": "8000",
        "GENERATED_API_PORT": "8001"
      }
    }
  }
}
```

### 2. Cursor IDE

For Cursor IDE integration:

1. Install the MCP extension (if available)
2. Add to `.cursor/mcp_config.json` in your project:

```json
{
  "servers": {
    "python-to-api": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_bridge"],
      "cwd": "${workspaceFolder}/mcp_server",
      "env": {
        "MCP_SERVER_PORT": "8000",
        "GENERATED_API_PORT": "8001"
      }
    }
  }
}
```

### 3. MCP CLI Client

For testing with the MCP CLI:

```bash
# Install MCP CLI
npm install -g @modelcontextprotocol/cli

# Connect to the server
mcp connect python -m mcp_server.mcp_bridge --cwd /path/to/mcp_server
```

### 4. Custom MCP Client

To connect a custom MCP client:

```python
import subprocess
import json
import asyncio

async def connect_to_mcp_server():
    # Start the MCP server process
    process = await asyncio.create_subprocess_exec(
        'python', '-m', 'mcp_server.mcp_bridge',
        cwd='/path/to/mcp_server',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={
            **os.environ,
            'MCP_SERVER_PORT': '8000',
            'GENERATED_API_PORT': '8001'
        }
    )
    
    # Send initialization request
    request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "clientInfo": {
                "name": "custom-client",
                "version": "1.0"
            }
        },
        "id": 1
    }
    
    process.stdin.write(json.dumps(request).encode() + b'\n')
    await process.stdin.drain()
    
    # Read response
    response = await process.stdout.readline()
    print(json.loads(response))
    
    return process
```

## Available MCP Tools

Once connected, the following tools are available:

### 1. `upload_python_file`
Upload a Python file to convert its functions to API endpoints.

```json
{
  "name": "upload_python_file",
  "arguments": {
    "file_path": "/path/to/your/script.py"
  }
}
```

Or with content directly:

```json
{
  "name": "upload_python_file",
  "arguments": {
    "content": "def add(x, y):\n    return int(x) + int(y)"
  }
}
```

### 2. `list_endpoints`
List all currently available API endpoints.

```json
{
  "name": "list_endpoints",
  "arguments": {}
}
```

### 3. `call_endpoint`
Call a generated API endpoint.

```json
{
  "name": "call_endpoint",
  "arguments": {
    "endpoint": "/add",
    "params": {
      "x": "5",
      "y": "3"
    }
  }
}
```

### 4. `get_server_status`
Get the status of the MCP server.

```json
{
  "name": "get_server_status",
  "arguments": {}
}
```

## MCP Resources

The server exposes these resources:

- `api://endpoints` - JSON list of all generated endpoints
- `api://swagger` - Link to Swagger UI documentation

## MCP Prompts

Available prompts:

- `convert_functions` - Interactive prompt to convert Python functions

## Example Conversation with Claude

Once connected, you can say:

> "Upload the file test_funcs.py and show me what endpoints were created"

Claude will use the MCP tools to:
1. Upload the file
2. List the generated endpoints
3. Show you the Swagger URL

> "Call the add endpoint with x=10 and y=20"

Claude will execute the API call and show the result.

## Troubleshooting

### Server not starting
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check logs in the MCP client

### Connection errors
- Verify the `cwd` path is correct
- Ensure no other process is using ports 8000/8001
- Check firewall settings

### Tools not appearing
- Restart the MCP client
- Check the server configuration syntax
- Verify the Python path is correct

## Security Considerations

- The server executes uploaded Python code - only use with trusted sources
- Consider running in a container or VM for isolation
- Add authentication for production use

## Development

To test the MCP bridge directly:

```bash
# Test initialization
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | python -m mcp_server.mcp_bridge

# Test listing tools
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}' | python -m mcp_server.mcp_bridge
```

## Next Steps

1. Configure your MCP client using the instructions above
2. Upload Python files with functions
3. Use the generated APIs through MCP tools
4. Access Swagger docs for interactive testing