# MCP Python-to-API Generator (MVP)

Upload any Python script with top-level functions. The orchestrator parses the functions and exposes each as a FastAPI endpoint with auto-generated Swagger docs.

## Quick Start

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

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