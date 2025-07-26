"""
Python Function Parser
=====================

Extract top-level function definitions from Python source code using AST.
Provides detailed metadata about function signatures, type hints, and documentation.
"""

import ast
from typing import Any, Dict, List, Optional, Union


def _extract_literal_value(node: ast.AST) -> str:
    """Extract a string representation of a literal value."""
    try:
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Str):
            return repr(node.s)
        elif isinstance(node, ast.Num):
            return repr(node.n)
        elif isinstance(node, ast.NameConstant):
            return repr(node.value)
        else:
            return ast.unparse(node)
    except Exception:
        return "None"


def _extract_type_hint(node: ast.arg) -> Optional[str]:
    """Extract type hint from function argument."""
    if node.annotation is None:
        return None
    
    try:
        return ast.unparse(node.annotation)
    except Exception:
        return None


def _extract_docstring(node: ast.FunctionDef) -> Optional[str]:
    """Extract docstring from function definition."""
    try:
        return ast.get_docstring(node)
    except Exception:
        return None


def extract_functions_from_source(source: str) -> List[Dict[str, Any]]:
    """
    Extract all top-level function definitions from Python source code.
    
    Args:
        source: Python source code as string
        
    Returns:
        List of function metadata dictionaries containing:
        - name: Function name
        - args: List of argument names
        - defaults: Dict of default values
        - type_hints: Dict of type hints
        - docstring: Function docstring
        - source: Original function source code
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}")
    
    functions = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Extract basic info
            name = node.name
            args_list = []
            type_hints = {}
            defaults = {}
            
            # Process arguments
            for arg in node.args.args:
                arg_name = arg.arg
                args_list.append(arg_name)
                
                # Extract type hint
                hint = _extract_type_hint(arg)
                if hint:
                    type_hints[arg_name] = hint
            
            # Process default values
            default_nodes = node.args.defaults
            if default_nodes:
                # Defaults align from the end
                arg_names_with_defaults = args_list[-len(default_nodes):]
                for arg_name, default_node in zip(arg_names_with_defaults, default_nodes):
                    defaults[arg_name] = _extract_literal_value(default_node)
            
            # Extract docstring
            docstring = _extract_docstring(node)
            
            # Extract source code
            try:
                function_source = ast.unparse(node)
            except Exception:
                function_source = f"def {name}(...):\n    pass"
            
            functions.append({
                "name": name,
                "args": args_list,
                "defaults": defaults,
                "type_hints": type_hints,
                "docstring": docstring,
                "source": function_source,
                "line_number": node.lineno if hasattr(node, 'lineno') else None
            })
    
    return functions


def validate_function(function_def: Dict[str, Any]) -> List[str]:
    """
    Validate a function definition and return any issues found.
    
    Args:
        function_def: Function metadata dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    required_fields = ["name", "args"]
    for field in required_fields:
        if field not in function_def:
            errors.append(f"Missing required field: {field}")
    
    # Validate function name
    if "name" in function_def:
        name = function_def["name"]
        if not name or not name.isidentifier():
            errors.append(f"Invalid function name: {name}")
    
    # Validate arguments
    if "args" in function_def:
        args = function_def["args"]
        if not isinstance(args, list):
            errors.append("Arguments must be a list")
        else:
            for i, arg in enumerate(args):
                if not isinstance(arg, str) or not arg.isidentifier():
                    errors.append(f"Invalid argument name at position {i}: {arg}")
    
    return errors


def get_function_signature(function_def: Dict[str, Any]) -> str:
    """
    Generate a readable function signature from function metadata.
    
    Args:
        function_def: Function metadata dictionary
        
    Returns:
        Formatted function signature string
    """
    name = function_def.get("name", "unknown")
    args = function_def.get("args", [])
    type_hints = function_def.get("type_hints", {})
    defaults = function_def.get("defaults", {})
    
    # Build argument list
    arg_parts = []
    for arg in args:
        arg_part = arg
        
        # Add type hint if available
        if arg in type_hints:
            arg_part += f": {type_hints[arg]}"
        
        # Add default value if available
        if arg in defaults:
            arg_part += f" = {defaults[arg]}"
        
        arg_parts.append(arg_part)
    
    # Build signature
    signature = f"def {name}({', '.join(arg_parts)})"
    
    # Add return type hint if available
    # Note: This would require parsing the function body for return annotations
    # For now, we'll skip this as it's more complex
    
    return signature


def filter_functions(functions: List[Dict[str, Any]], 
                    min_args: int = 0,
                    max_args: Optional[int] = None,
                    has_docstring: Optional[bool] = None,
                    has_type_hints: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Filter functions based on various criteria.
    
    Args:
        functions: List of function metadata dictionaries
        min_args: Minimum number of arguments
        max_args: Maximum number of arguments (None for no limit)
        has_docstring: Filter by presence of docstring
        has_type_hints: Filter by presence of type hints
        
    Returns:
        Filtered list of functions
    """
    filtered = []
    
    for func in functions:
        # Check argument count
        arg_count = len(func.get("args", []))
        if arg_count < min_args:
            continue
        if max_args is not None and arg_count > max_args:
            continue
        
        # Check docstring
        if has_docstring is not None:
            has_doc = func.get("docstring") is not None
            if has_doc != has_docstring:
                continue
        
        # Check type hints
        if has_type_hints is not None:
            has_hints = len(func.get("type_hints", {})) > 0
            if has_hints != has_type_hints:
                continue
        
        filtered.append(func)
    
    return filtered 