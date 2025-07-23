# MCP Python-to-API Generator (MVP)

Upload any Python script with top-level functions. The orchestrator parses the functions and exposes each as a FastAPI endpoint with auto-generated Swagger docs.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

Upload a Python script

curl -F "file=@examples/sample_funcs.py" http://localhost:8000/upload

Response

{
  "message": "Endpoints created.",
  "swagger_url": "http://localhost:8001/docs",
  "openapi_url": "http://localhost:8001/openapi.json",
  "endpoints": ["/add", "/subtract"]
}

Open the Swagger URL in a browser to test your functions.

---

## How It Works
1. /upload accepts .py
2. We AST-parse top-level def functions
3. Generate generated_fastapi_app.py
4. Restart a uvicorn subprocess serving those endpoints
5. Reply with test URLs

---

## Limitations (MVP)
- Query params only; all strings coerced at runtime
- No nested imports resolution
- No security / sandboxing
- Single upload at a time (latest wins)

---

## Roadmap
- Type hints → Pydantic models
- POST for complex JSON bodies
- Auth / sandboxing
- Multi-file module support
- Versioned APIs
- Async function support

---

## Test It Fast

Create `test_funcs.py`:
```python
def add(x, y):
    "Add two numbers."
    return int(x) + int(y)

def greet(name="world"):
    return f"Hello, {name}!"
```

Upload:

curl -F "file=@test_funcs.py" http://localhost:8000/upload

Then visit http://localhost:8001/docs.