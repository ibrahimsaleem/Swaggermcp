"""
MCP → FastAPI **Simplest Reload** (v1.1)
=====================================
* Exactly **one** Uvicorn server on port 8001.
* We launch it **once** with `--reload` so every time the tool overwrites
  `generated_fastapi_app.py` the server auto‑refreshes.
* Swagger UI is always at `http://localhost:8001/docs`.

This fixes the "old endpoints still show" issue on Windows where the port isn’t
freed quickly enough.

---
Usage
-----
1. **Start the MCP server** (Cursor spawns it via stdio):
   ```bash
   python mcp_simpler.py
   ```
2. **Call the tool** with new code; just refresh Swagger—no manual restarts.

Dependencies
------------
```bash
pip install fastapi uvicorn mcp-server
```
"""
from __future__ import annotations

import ast
import subprocess
import sys
import atexit
from pathlib import Path
from typing import Any, List

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# ───────────────────────── Config ─────────────────────────
PORT = 8001
BASE_DIR = Path(__file__).parent.resolve()
APP_PATH = BASE_DIR / "generated_fastapi_app.py"
SERVER_PROC: subprocess.Popen | None = None

# ─────────────────── Code Generation ────────────────────

def _parse_functions(source: str) -> List[ast.FunctionDef]:
    return [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)]


def _build_app_source(fns: List[ast.FunctionDef]) -> str:
    user_src = "\n\n".join(ast.unparse(fn) for fn in fns)
    lines = [
        "from fastapi import FastAPI, HTTPException",
        "from typing import Any",
        "",
        "app = FastAPI(title='MCP Generated API', docs_url='/docs')",
        "",
        "# >>> USER CODE >>>",
        user_src.rstrip(),
        "# <<< USER CODE <<<",
        "",
    ]
    for fn in fns:
        name = fn.name
        params = [p.arg for p in fn.args.args]
        param_sig = ", ".join(f"{p}: Any" for p in params) or "_dummy: Any = None"
        arg_list = ", ".join(params)
        lines.append(
            f"""\n@app.post('/{name}')\nasync def {name}_endpoint({param_sig}):\n    try:\n        result = {name}({arg_list})\n        return {{'result': result}}\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=str(e))\n"""
        )
    return "\n".join(lines)

# ─────────────── Uvicorn Lifecycle Helpers ───────────────

def _ensure_server_running():
    global SERVER_PROC
    if SERVER_PROC and SERVER_PROC.poll() is None:
        return  # already live with --reload

    SERVER_PROC = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            f"{APP_PATH.stem}:app",
            "--reload",
            "--port",
            str(PORT),
        ],
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _cleanup():
    if SERVER_PROC and SERVER_PROC.poll() is None:
        SERVER_PROC.terminate()
atexit.register(_cleanup)

# ─────────────────────── MCP Tool ────────────────────────

mcp = FastMCP(name="SimpleSwaggerMCP")

@mcp.tool()
async def convert_python_to_api(source_code: str) -> TextContent:  # noqa: D401
    """Overwrite the FastAPI app with new endpoints and rely on `--reload`."""

    fns = _parse_functions(source_code)
    if not fns:
        return TextContent(type="text", text="⚠️ No top‑level functions found.")

    APP_PATH.write_text(_build_app_source(fns), encoding="utf‑8")
    _ensure_server_running()  # first call launches server; later writes trigger reload

    endpoints = ", ".join(f"/{fn.name}" for fn in fns)
    return TextContent(
        type="text",
        text=(
            "✅ API updated!\n\n"
            "Swagger UI: http://localhost:8001/docs\n"
            f"Endpoints: {endpoints}\n"
            "(Just refresh Swagger to see the new list.)"
        ),
    )

# ───────────────────── Entrypoint ─────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
