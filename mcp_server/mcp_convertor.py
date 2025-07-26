"""
MCP Swagger Converter Server
===========================
A minimal MCP (Model‑Control‑Protocol) server exposing **one tool**:
`convert_python_to_api`.

Send raw Python source code and get back a ready‑to‑run FastAPI app
(`generated_fastapi_app.py`) that turns EVERY top‑level function into a
JSON endpoint PLUS an auto‑generated Swagger UI.

Run the MCP server first:
    python mcp_swagger_converter.py  # runs over stdio by default

Then, after a successful conversion, start the generated API:
    uvicorn generated_fastapi_app:app --reload --port 8001
The Swagger UI will be live at http://localhost:8001/docs

Dependencies (⇢ keep them light):
    pip install fastapi uvicorn mcp‐server
"""
from __future__ import annotations

import ast
import textwrap
from pathlib import Path
from typing import Any, List

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# ────────────────────────── Helper functions ──────────────────────────

def extract_functions_from_source(source: str) -> List[ast.FunctionDef]:
    """Return a list of *top‑level* ``ast.FunctionDef`` objects."""
    module_node = ast.parse(source)
    return [n for n in module_node.body if isinstance(n, ast.FunctionDef)]


def generate_fastapi_app_source(source: str, functions: List[ast.FunctionDef]) -> str:
    """Create a FastAPI app string exposing each function at **POST /<name>**."""

    header = [
        "from fastapi import FastAPI, HTTPException",
        "from typing import Any",
        "",
        "# >>> USER CODE >>>",
        source.rstrip(),
        "# <<< USER CODE <<<",
        "",
        "app = FastAPI(title='Generated API')",
        "",
    ]

    for fn in functions:
        fn_name = fn.name
        params = [p.arg for p in fn.args.args]
        param_sig = ", ".join(f"{p}: Any" for p in params) or "_dummy: Any = None"  # FastAPI needs ≥1 param
        arg_list = ", ".join(params)
        endpoint_src = textwrap.dedent(
            f"""
            @app.post('/{fn_name}')
            async def {fn_name}_endpoint({param_sig}):
                try:
                    result = {fn_name}({arg_list})
                    return {{'result': result}}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            """
        )
        header.append(endpoint_src.rstrip())
    return "\n".join(header) + "\n"


# ────────────────────────────── MCP Server ─────────────────────────────

mcp = FastMCP(name="SwaggerConverterMCP")


@mcp.tool()
async def convert_python_to_api(source_code: str) -> TextContent:  # noqa: D401
    """Turn raw Python *source_code* into a FastAPI Swagger app and respond with instructions."""

    functions = extract_functions_from_source(source_code)
    if not functions:
        return TextContent(
            type="text",
            text="⚠️ No top‑level functions found. Nothing to expose.",
        )

    generated_app_source = generate_fastapi_app_source(source_code, functions)
    out_path = Path(__file__).with_name("generated_fastapi_app.py")
    out_path.write_text(generated_app_source, encoding="utf‑8")

    endpoints = ", ".join(f"/{fn.name}" for fn in functions)
    swagger_url = "http://localhost:8001/docs"

    reply = (
        "✅ API generated successfully!\n\n"
        f"Saved as: {out_path.name}\n"
        f"Endpoints: {endpoints}\n"
        f"Run:  uvicorn {out_path.stem}:app --reload --port 8001\n"
        f"Swagger: {swagger_url}"
    )
    return TextContent(type="text", text=reply)


# ────────────────────────────── Entrypoint ─────────────────────────────

if __name__ == "__main__":
    # Use stdio transport for CLI‑style tool use; switch to streamable‑http if desired.
    mcp.run(transport="stdio")
