"""
MCP → FastAPI **Simplest Reload** (v1.2)
=====================================
* **One** Uvicorn server on port 8001, launched once with `--reload`.
* Each call to `convert_python_to_api` overwrites `generated_fastapi_app.py`; the
  server hot‑reloads automatically.
* Swagger UI is always at `http://localhost:8001/docs`.
* **NEW TOOLS**
  * `restart_server` – kills and restarts Uvicorn in case hot‑reload gets
    stuck.
  * `test_endpoints` – pings every endpoint in the current API and reports
    which ones returned HTTP 200.

Usage
-----
```text
1. convert_python_to_api(<your code>)   # generates or replaces endpoints
2. test_endpoints()                     # quick health‑check
3. restart_server()                     # if step 2 shows failures
```

Dependencies
------------
```bash
pip install fastapi uvicorn mcp-server requests
```
"""
from __future__ import annotations

import ast
import subprocess
import sys
import atexit
from pathlib import Path
from typing import Any, List, Dict

import requests
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


def _restart_server_proc():
    global SERVER_PROC
    if SERVER_PROC and SERVER_PROC.poll() is None:
        SERVER_PROC.terminate()
        try:
            SERVER_PROC.wait(timeout=3)
        except subprocess.TimeoutExpired:
            SERVER_PROC.kill()
    SERVER_PROC = None
    _ensure_server_running()


def _cleanup():
    if SERVER_PROC and SERVER_PROC.poll() is None:
        SERVER_PROC.terminate()
atexit.register(_cleanup)

# ─────────────────────── MCP Tools ───────────────────────

mcp = FastMCP(name="SimpleSwaggerMCP")

@mcp.tool()
async def convert_python_to_api(source_code: str) -> TextContent:
    """Overwrite the FastAPI app with new endpoints and rely on `--reload`."""

    fns = _parse_functions(source_code)
    if not fns:
        return TextContent(type="text", text="⚠️ No top‑level functions found.")

    APP_PATH.write_text(_build_app_source(fns), encoding="utf‑8")
    _ensure_server_running()

    endpoints = ", ".join(f"/{fn.name}" for fn in fns)
    return TextContent(
        type="text",
        text=(
            "✅ API updated!\n\n"
            "Swagger UI: http://localhost:8001/docs\n"
            f"Endpoints: {endpoints}\n"
            "(Refresh Swagger to see the latest list.)"
        ),
    )


@mcp.tool()
async def restart_server() -> TextContent:
    """Force‑restart Uvicorn (use if hot‑reload gets stuck)."""
    _restart_server_proc()
    return TextContent(type="text", text="🔄 Uvicorn restarted on port 8001. Refresh Swagger.")


@mcp.tool()
async def test_endpoints() -> TextContent:
    """Ping every endpoint and report which ones returned HTTP 200."""
    try:
        spec = requests.get(f"http://localhost:{PORT}/openapi.json", timeout=2).json()
    except Exception as e:
        return TextContent(type="text", text=f"❌ Could not fetch OpenAPI spec: {e}")

    results: Dict[str, str] = {}
    for path, methods in spec.get("paths", {}).items():
        if "post" not in methods:
            continue  # we only generate POST routes
        url = f"http://localhost:{PORT}{path}"
        try:
            r = requests.post(url, json={}, timeout=2)
            results[path] = "✅ 200" if r.status_code == 200 else f"⚠️ {r.status_code}"
        except Exception as e:
            results[path] = f"❌ {e.__class__.__name__}"

    report_lines = [f"{status}  {path}" for path, status in results.items()] or ["(no endpoints)"]
    return TextContent(type="text", text="\n".join(report_lines))

# ───────────────────── Entrypoint ─────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
