"""
MCP Orchestration Server

Accepts Python file uploads, parses top-level functions, generates
FastAPI endpoints in `generated_fastapi_app.py`, restarts the dynamic
API server, and returns the Swagger URL + endpoint list.

Run:
    uvicorn main:app --reload --port 8000

Upload via:
    curl -F "file=@your_script.py" http://localhost:8000/upload

Response:
    {
      "message": "Endpoints created",
      "swagger_url": "http://localhost:8001/docs",
      "endpoints": ["/add", "/foo"]
    }
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from utils.code_parser import extract_functions_from_source
from utils.fastapi_writer import generate_fastapi_app_source
from utils.runner import APIServerRunner

BASE_DIR = Path(__file__).parent.resolve()
GENERATED_APP_PATH = BASE_DIR / "generated_fastapi_app.py"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Runner instance (global, single)
runner = APIServerRunner(app_module_path=GENERATED_APP_PATH, port=8001)

app = FastAPI(
    title="MCP Conversion Orchestrator",
    description="Upload a Python script; get auto-generated FastAPI endpoints + Swagger.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup():
    # Ensure there's *some* generated app in place so runner can start
    if not GENERATED_APP_PATH.exists():
        GENERATED_APP_PATH.write_text("from fastapi import FastAPI\n\napp = FastAPI(title='Generated API (empty)')\n")
    runner.start()  # start initial server (empty)


@app.on_event("shutdown")
async def shutdown():
    runner.stop()


@app.post("/upload")
async def upload_python_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    # Save uploaded file
    temp_path = UPLOADS_DIR / file.filename
    with temp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Read source
    source = temp_path.read_text()

    # Parse functions
    try:
        func_defs = extract_functions_from_source(source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse functions: {e}")

    if not func_defs:
        raise HTTPException(status_code=400, detail="No top-level functions found in uploaded file.")

    # Generate dynamic API source
    try:
        generated_source, endpoint_paths = generate_fastapi_app_source(
            raw_source=source,
            functions=func_defs,
            app_title=f"Generated API from {file.filename}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate API: {e}")

    # Write generated file
    GENERATED_APP_PATH.write_text(generated_source)

    # Restart server
    runner.restart()

    return JSONResponse(
        {
            "message": "Endpoints created.",
            "swagger_url": f"http://localhost:{runner.port}/docs",
            "openapi_url": f"http://localhost:{runner.port}/openapi.json",
            "endpoints": endpoint_paths,
            "source_saved_as": str(temp_path.name),
        }
    )


@app.get("/status")
async def status():
    return {
        "runner_alive": runner.is_running(),
        "generated_app_path": str(GENERATED_APP_PATH),
        "swagger_url": f"http://localhost:{runner.port}/docs",
    }