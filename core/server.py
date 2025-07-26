"""
SwaggerMCP - Main Server
=======================

A unified server that provides both FastAPI endpoints and MCP integration
for converting Python functions to REST APIs with automatic Swagger documentation.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.parser import extract_functions_from_source
from utils.generator import generate_fastapi_app_source
from utils.runner import APIServerRunner

# Configuration
PORT = int(os.getenv("PORT", "8000"))
API_PORT = int(os.getenv("API_PORT", "8001"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Paths
BASE_DIR = Path(__file__).parent
GENERATED_APP_PATH = BASE_DIR / "generated_api.py"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Global server runner
api_runner = APIServerRunner(app_module_path=GENERATED_APP_PATH, port=API_PORT)

# FastAPI app
app = FastAPI(
    title="SwaggerMCP Server",
    description="Convert Python functions to REST APIs with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# MCP server
mcp = FastMCP(name="SwaggerMCP")

@app.on_event("startup")
async def startup_event():
    """Initialize the server on startup."""
    # Ensure generated app exists
    if not GENERATED_APP_PATH.exists():
        GENERATED_APP_PATH.write_text("""
from fastapi import FastAPI
app = FastAPI(title="SwaggerMCP Generated API")
""")
    
    # Start API server
    api_runner.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    api_runner.stop()

# ============================================================================
# FastAPI Endpoints
# ============================================================================

@app.post("/upload")
async def upload_python_file(file: UploadFile = File(...)):
    """Upload a Python file and convert its functions to API endpoints."""
    
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted")
    
    # Save uploaded file
    file_path = UPLOADS_DIR / file.filename
    with file_path.open("wb") as f:
        content = await file.read()
        f.write(content)
    
    # Read and parse source
    source = content.decode("utf-8")
    
    try:
        functions = extract_functions_from_source(source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse functions: {e}")
    
    if not functions:
        raise HTTPException(status_code=400, detail="No top-level functions found")
    
    # Generate API
    try:
        generated_source, endpoints = generate_fastapi_app_source(
            raw_source=source,
            functions=functions,
            app_title=f"API from {file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate API: {e}")
    
    # Write generated file and restart server
    GENERATED_APP_PATH.write_text(generated_source)
    api_runner.restart()
    
    return JSONResponse({
        "message": "API generated successfully",
        "swagger_url": f"http://localhost:{API_PORT}/docs",
        "openapi_url": f"http://localhost:{API_PORT}/openapi.json",
        "endpoints": endpoints,
        "file_saved": str(file_path.name)
    })

@app.get("/status")
async def get_status():
    """Get server status and health information."""
    return {
        "server": "running",
        "api_server": "running" if api_runner.is_running() else "stopped",
        "swagger_url": f"http://localhost:{API_PORT}/docs",
        "port": PORT,
        "api_port": API_PORT,
        "debug": DEBUG
    }

@app.get("/endpoints")
async def list_endpoints():
    """List all available API endpoints."""
    try:
        import requests
        response = requests.get(f"http://localhost:{API_PORT}/openapi.json", timeout=2)
        if response.status_code == 200:
            spec = response.json()
            endpoints = list(spec.get("paths", {}).keys())
            return {"endpoints": endpoints}
        else:
            return {"endpoints": [], "error": "Could not fetch endpoints"}
    except Exception as e:
        return {"endpoints": [], "error": str(e)}

# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
async def convert_python_to_api(source_code: str, group: Optional[str] = None) -> TextContent:
    """Convert Python code to API endpoints with automatic Swagger documentation."""
    
    try:
        # Parse functions
        functions = extract_functions_from_source(source_code)
        
        if not functions:
            return TextContent(
                type="text",
                text="⚠️ No top-level functions found in the provided code."
            )
        
        # Generate API
        generated_source, endpoints = generate_fastapi_app_source(
            raw_source=source_code,
            functions=functions,
            app_title=f"Generated API{f' - {group}' if group else ''}"
        )
        
        # Write and restart
        GENERATED_APP_PATH.write_text(generated_source)
        api_runner.restart()
        
        # Format response
        endpoint_list = ", ".join(endpoints)
        response_text = f"""✅ API generated successfully!

🌐 Swagger UI: http://localhost:{API_PORT}/docs
📋 OpenAPI Spec: http://localhost:{API_PORT}/openapi.json
🔗 Endpoints: {endpoint_list}

💡 Tip: Refresh the Swagger UI to see the latest endpoints."""
        
        return TextContent(type="text", text=response_text)
        
    except Exception as e:
        return TextContent(
            type="text",
            text=f"❌ Error generating API: {str(e)}"
        )

@mcp.tool()
async def restart_server(random_string: str) -> TextContent:
    """Restart the API server to ensure all endpoints are loaded."""
    
    try:
        api_runner.restart()
        return TextContent(
            type="text",
            text=f"🔄 API server restarted successfully on port {API_PORT}.\nRefresh the Swagger UI to see updates."
        )
    except Exception as e:
        return TextContent(
            type="text",
            text=f"❌ Error restarting server: {str(e)}"
        )

@mcp.tool()
async def test_endpoints(random_string: str) -> TextContent:
    """Test all available endpoints and report their status."""
    
    try:
        import requests
        
        # Get OpenAPI spec
        response = requests.get(f"http://localhost:{API_PORT}/openapi.json", timeout=5)
        if response.status_code != 200:
            return TextContent(
                type="text",
                text=f"❌ Could not fetch API specification (Status: {response.status_code})"
            )
        
        spec = response.json()
        results = []
        
        # Test each endpoint
        for path, methods in spec.get("paths", {}).items():
            if "post" in methods:
                try:
                    test_response = requests.post(
                        f"http://localhost:{API_PORT}{path}",
                        json={},
                        timeout=3
                    )
                    status = "✅ 200" if test_response.status_code == 200 else f"⚠️ {test_response.status_code}"
                except Exception as e:
                    status = f"❌ {type(e).__name__}"
                
                results.append(f"{status} {path}")
        
        if not results:
            return TextContent(type="text", text="📭 No endpoints found to test.")
        
        return TextContent(
            type="text",
            text="🧪 Endpoint Test Results:\n" + "\n".join(results)
        )
        
    except Exception as e:
        return TextContent(
            type="text",
            text=f"❌ Error testing endpoints: {str(e)}"
        )

@mcp.tool()
async def list_endpoints() -> TextContent:
    """List all currently available API endpoints."""
    
    try:
        import requests
        
        response = requests.get(f"http://localhost:{API_PORT}/openapi.json", timeout=3)
        if response.status_code == 200:
            spec = response.json()
            endpoints = list(spec.get("paths", {}).keys())
            
            if endpoints:
                endpoint_list = "\n".join(f"• {endpoint}" for endpoint in endpoints)
                return TextContent(
                    type="text",
                    text=f"📋 Available Endpoints:\n{endpoint_list}\n\n🌐 Swagger UI: http://localhost:{API_PORT}/docs"
                )
            else:
                return TextContent(
                    type="text",
                    text="📭 No endpoints available.\nUse `convert_python_to_api` to create some!"
                )
        else:
            return TextContent(
                type="text",
                text=f"❌ Could not fetch endpoints (Status: {response.status_code})"
            )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"❌ Error listing endpoints: {str(e)}"
        )

@mcp.tool()
async def get_server_status() -> TextContent:
    """Get the current status of the SwaggerMCP server."""
    
    status_info = {
        "main_server": "✅ Running",
        "api_server": "✅ Running" if api_runner.is_running() else "❌ Stopped",
        "port": PORT,
        "api_port": API_PORT,
        "swagger_url": f"http://localhost:{API_PORT}/docs"
    }
    
    status_text = "🖥️ Server Status:\n"
    for key, value in status_info.items():
        if key == "swagger_url":
            status_text += f"🌐 {key}: {value}\n"
        else:
            status_text += f"• {key}: {value}\n"
    
    return TextContent(type="text", text=status_text)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the server."""
    import uvicorn
    
    print("🚀 Starting SwaggerMCP Server...")
    print(f"📡 Main Server: http://localhost:{PORT}")
    print(f"🌐 API Server: http://localhost:{API_PORT}")
    print(f"📚 Swagger UI: http://localhost:{API_PORT}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "core.server:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )

if __name__ == "__main__":
    main() 