"""
Extract top-level function definitions from Python source using AST.

Returns a list of function metadata dicts:
[
  {
    "name": "add",
    "args": ["x", "y"],
    "defaults": { "y": "10" },  # literal string form
    "type_hints": { "x": "int", "y": "int" },  # best effort (optional)
    "docstring": "Adds two numbers."
  },
  ...
]
"""
import ast
from typing import Any, Dict, List, Optional

def _literal_or_str(node: ast.AST) -> str:
    """Try to produce a source-ish string for a default value."""
    try:
        if isinstance(node, ast.Constant):
            return repr(node.value)
        # fallback: reconstruct rough code
        return ast.unparse(node)  # Python 3.9+
    except Exception:
        return "None"

def _extract_type_hint(arg: ast.arg) -> Optional[str]:
    if arg.annotation is None:
        return None
    try:
        return ast.unparse(arg.annotation)
    except Exception:
        return None

def extract_functions_from_source(source: str) -> List[Dict[str, Any]]:
    tree = ast.parse(source)
    funcs: List[Dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name

            # Positional/keyword args
            args_list = []
            type_hints = {}
            defaults = {}

            # Collect args
            for arg in node.args.args:
                arg_name = arg.arg
                args_list.append(arg_name)
                hint = _extract_type_hint(arg)
                if hint:
                    type_hints[arg_name] = hint

            # Default mapping (align from end)
            default_nodes = node.args.defaults
            if default_nodes:
                arg_names_with_defaults = args_list[-len(default_nodes):]
                for arg_name, default_node in zip(arg_names_with_defaults, default_nodes):
                    defaults[arg_name] = _literal_or_str(default_node)

            # Docstring
            docstring = ast.get_docstring(node)

            funcs.append(
                {
                    "name": name,
                    "args": args_list,
                    "defaults": defaults,
                    "type_hints": type_hints,
                    "docstring": docstring,
                }
            )
    return funcs