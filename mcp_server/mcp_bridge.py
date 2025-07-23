#!/usr/bin/env python3
"""
MCP Bridge - Implements Model Context Protocol for the Python-to-API server.

This bridge allows MCP clients (like Claude Desktop) to:
1. Upload Python files and convert them to APIs
2. Query available endpoints
3. Execute API calls through the MCP protocol
"""

import json
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
import requests
import tempfile
import os
from pathlib import Path
from security import safe_requests, safe_command

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation for Python-to-API conversion."""
    
    def __init__(self):
        self.server_port = os.getenv("MCP_SERVER_PORT", "8000")
        self.api_port = os.getenv("GENERATED_API_PORT", "8001")
        self.base_url = f"http://localhost:{self.server_port}"
        self.api_base_url = f"http://localhost:{self.api_port}"
        self.current_endpoints = []
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                return self._create_response(request_id, {
                    "protocolVersion": "1.0",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "python-to-api-mcp-server",
                        "version": "0.1.0"
                    }
                })
            
            elif method == "tools/list":
                return self._create_response(request_id, {
                    "tools": [
                        {
                            "name": "upload_python_file",
                            "description": "Upload a Python file to convert its functions to API endpoints",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {
                                        "type": "string",
                                        "description": "Path to the Python file to upload"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Python code content (alternative to file_path)"
                                    }
                                },
                                "oneOf": [
                                    {"required": ["file_path"]},
                                    {"required": ["content"]}
                                ]
                            }
                        },
                        {
                            "name": "list_endpoints",
                            "description": "List all currently available API endpoints",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "call_endpoint",
                            "description": "Call a generated API endpoint",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "endpoint": {
                                        "type": "string",
                                        "description": "The endpoint path (e.g., '/add')"
                                    },
                                    "params": {
                                        "type": "object",
                                        "description": "Query parameters for the endpoint"
                                    }
                                },
                                "required": ["endpoint", "params"]
                            }
                        },
                        {
                            "name": "get_server_status",
                            "description": "Get the status of the MCP server and generated API",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                })
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "upload_python_file":
                    result = await self._upload_python_file(arguments)
                elif tool_name == "list_endpoints":
                    result = await self._list_endpoints()
                elif tool_name == "call_endpoint":
                    result = await self._call_endpoint(arguments)
                elif tool_name == "get_server_status":
                    result = await self._get_server_status()
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return self._create_response(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                })
            
            elif method == "resources/list":
                return self._create_response(request_id, {
                    "resources": [
                        {
                            "uri": "api://endpoints",
                            "name": "Generated API Endpoints",
                            "description": "List of all generated API endpoints",
                            "mimeType": "application/json"
                        },
                        {
                            "uri": "api://swagger",
                            "name": "Swagger Documentation",
                            "description": "Link to Swagger UI for generated APIs",
                            "mimeType": "text/plain"
                        }
                    ]
                })
            
            elif method == "resources/read":
                uri = params.get("uri", "")
                if uri == "api://endpoints":
                    endpoints = await self._list_endpoints()
                    return self._create_response(request_id, {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(endpoints, indent=2)
                            }
                        ]
                    })
                elif uri == "api://swagger":
                    return self._create_response(request_id, {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/plain",
                                "text": f"Swagger UI available at: {self.api_base_url}/docs"
                            }
                        ]
                    })
            
            elif method == "prompts/list":
                return self._create_response(request_id, {
                    "prompts": [
                        {
                            "name": "convert_functions",
                            "description": "Convert Python functions to API endpoints",
                            "arguments": [
                                {
                                    "name": "functions",
                                    "description": "Python code containing functions to convert",
                                    "required": True
                                }
                            ]
                        }
                    ]
                })
            
            elif method == "prompts/get":
                prompt_name = params.get("name")
                if prompt_name == "convert_functions":
                    functions = params.get("arguments", {}).get("functions", "")
                    return self._create_response(request_id, {
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": f"Please convert these Python functions to API endpoints:\n\n```python\n{functions}\n```"
                                }
                            }
                        ]
                    })
            
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._create_error_response(request_id, str(e))
    
    async def _upload_python_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a Python file to the server."""
        if "file_path" in arguments:
            # Upload from file path
            file_path = arguments["file_path"]
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "text/x-python")}
                response = requests.post(f"{self.base_url}/upload", files=files, timeout=60)
        
        elif "content" in arguments:
            # Upload from content
            content = arguments["content"]
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                with open(temp_path, "rb") as f:
                    files = {"file": ("uploaded_code.py", f, "text/x-python")}
                    response = requests.post(f"{self.base_url}/upload", files=files, timeout=60)
            finally:
                os.unlink(temp_path)
        
        else:
            raise ValueError("Either 'file_path' or 'content' must be provided")
        
        if response.status_code == 200:
            result = response.json()
            self.current_endpoints = result.get("endpoints", [])
            return result
        else:
            raise ValueError(f"Upload failed: {response.text}")
    
    async def _list_endpoints(self) -> Dict[str, Any]:
        """List all available endpoints."""
        return {
            "endpoints": self.current_endpoints,
            "swagger_url": f"{self.api_base_url}/docs",
            "openapi_url": f"{self.api_base_url}/openapi.json"
        }
    
    async def _call_endpoint(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a generated API endpoint."""
        endpoint = arguments.get("endpoint", "")
        params = arguments.get("params", {})
        
        url = f"{self.api_base_url}{endpoint}"
        response = safe_requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"API call failed: {response.text}")
    
    async def _get_server_status(self) -> Dict[str, Any]:
        """Get server status."""
        try:
            response = safe_requests.get(f"{self.base_url}/status", timeout=60)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to get status", "details": response.text}
        except Exception as e:
            return {"error": "Server not reachable", "details": str(e)}
    
    def _create_response(self, request_id: Optional[Any], result: Any) -> Dict[str, Any]:
        """Create a standard MCP response."""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if request_id is not None:
            response["id"] = request_id
        return response
    
    def _create_error_response(self, request_id: Optional[Any], error_message: str) -> Dict[str, Any]:
        """Create an error response."""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": error_message
            }
        }
        if request_id is not None:
            response["id"] = request_id
        return response

async def run_mcp_server():
    """Run the MCP server, reading from stdin and writing to stdout."""
    server = MCPServer()
    
    # First, ensure the FastAPI server is running
    logger.info("Starting Python-to-API FastAPI server...")
    import subprocess
    import time
    
    # Start the FastAPI server in the background
    server_process = safe_command.run(subprocess.Popen, [sys.executable, "-m", "uvicorn", "main:app", "--port", server.server_port],
        cwd=Path(__file__).parent
    )
    
    # Give it time to start
    time.sleep(3)
    
    logger.info("MCP Bridge ready for requests")
    
    try:
        # Read JSON-RPC messages from stdin
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            try:
                # Read line from stdin
                line = await reader.readline()
                if not line:
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line.decode().strip())
                logger.info(f"Received request: {request.get('method', 'unknown')}")
                
                # Handle request
                response = await server.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response), flush=True)
    
    finally:
        # Clean up
        logger.info("Shutting down...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(run_mcp_server())
