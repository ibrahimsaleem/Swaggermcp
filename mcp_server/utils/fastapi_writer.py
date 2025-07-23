"""
Generate FastAPI source code that:
- Imports the user source (inlined for MVP)
- Re-exports a FastAPI app with one GET endpoint per function
- Performs basic type coercion of query params
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple

IMPORT_NOTE = """# === AUTO-GENERATED FILE ===
# DO NOT EDIT BY HAND. Regenerated each upload.
# This file contains:
#   - The user's uploaded Python source
#   - FastAPI endpoints exposing each top-level function
#
# Regeneration Strategy:
# - Each upload replaces entire file.
# - Endpoints use query parameters (strings) and attempt runtime type coercion.
#
# Security Note:
#   Executing uploaded code is dangerous. Use sandboxing in production.
"""

TYPE_COERCE_FN = r"""
def _coerce_param(value: str):
    # Try int
    try:
        return int(value)
    except Exception:
        pass
    # Try float
    try:
        return float(value)
    except Exception:
        pass
    # Try bool
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    # Try JSON literal
    try:
        import json
        return json.loads(value)
    except Exception:
        pass
    # Fallback string
    return value
"""

def generate_fastapi_app_source(
    raw_source: str,
    functions: List[Dict[str, Any]],
    app_title: str = "Generated API",
) -> Tuple[str, List[str]]:
    """
    Produce Python source for `generated_fastapi_app.py`.
    Returns: (source_code, endpoint_paths)
    """
    # Build endpoint code
    endpoint_blocks = []
    endpoint_paths = []
    for fmeta in functions:
        fname = fmeta["name"]
        args = fmeta["args"]
        doc = fmeta.get("docstring") or ""
        endpoint_path = f"/{fname}"
        endpoint_paths.append(endpoint_path)

        # Build param signature for FastAPI function: all str (query params)
        if args:
            param_sig = ", ".join([f"{a}: str" for a in args])
        else:
            param_sig = ""

        # Build conversion + call body
        # We'll build arglist expression: coerce each
        if args:
            coerced_args_expr = ", ".join([f"_coerce_param({a})" for a in args])
        else:
            coerced_args_expr = ""

        endpoint_block = f"""
@app.get("{endpoint_path}", summary="{fname}", description={repr(doc)})
def {fname}_endpoint({param_sig}):
    try:
        result = {fname}({coerced_args_expr})
    except Exception as e:
        return {{"error": str(e)}}
    return {{"result": result}}
"""
        endpoint_blocks.append(endpoint_block)

    # Build final code
    code = f"""{IMPORT_NOTE}

from fastapi import FastAPI

app = FastAPI(title={repr(app_title)})

{TYPE_COERCE_FN}

# === USER SOURCE START ===
{raw_source}
# === USER SOURCE END ===

# === GENERATED ENDPOINTS ===
"""
    code += "\n".join(endpoint_blocks)
    code += "\n"

    return code, endpoint_paths