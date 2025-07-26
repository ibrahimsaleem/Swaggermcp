# 🚀 SwaggerMCP - AI-Powered Python to API Generator

> **Transform Python functions into REST APIs instantly with AI assistance**

SwaggerMCP is a powerful tool that automatically converts Python functions into REST API endpoints with full Swagger documentation. It features seamless Model Context Protocol (MCP) integration, allowing AI assistants like Claude to directly create and manage APIs.

## ✨ Features

- 🔄 **Instant API Generation** - Convert Python functions to REST endpoints in seconds
- 🤖 **AI Integration** - Full MCP support for Claude, Cursor, and other AI assistants
- 📚 **Auto Documentation** - Automatic Swagger UI generation
- 🧪 **Live Testing** - Built-in endpoint testing and validation
- 🔧 **Hot Reload** - Real-time API updates without server restarts
- 🐳 **Docker Ready** - Containerized deployment support

## 🏗️ Architecture

```
SwaggerMCP/
├── 📁 core/                    # Core server components
│   ├── server.py              # Main FastAPI server
│   ├── mcp_bridge.py          # MCP protocol implementation
│   └── converter.py           # Python to API converter
├── 📁 utils/                   # Utility modules
│   ├── parser.py              # AST-based code parsing
│   ├── generator.py           # FastAPI code generation
│   └── runner.py              # Server lifecycle management
├── 📁 configs/                 # Configuration files
│   ├── cursor.json            # Cursor IDE setup
│   ├── claude.json            # Claude Desktop setup
│   └── docker.json            # Docker configuration
├── 📁 examples/                # Example functions and demos
│   ├── math_functions.py      # Mathematical operations
│   ├── string_utils.py        # String manipulation
│   └── algorithms.py          # Algorithm implementations
├── 📁 docs/                    # Documentation
├── 🐳 Dockerfile              # Container configuration
├── 📋 requirements.txt        # Python dependencies
└── 📖 README.md               # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ibrahimsaleem/Swaggermcp.git
cd Swaggermcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Start the MCP server
python core/server.py

# Or use Docker
docker build -t swaggermcp .
docker run -p 8000:8000 -p 8001:8001 swaggermcp
```

### 3. Connect AI Assistant

#### Cursor IDE Setup

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "swaggermcp": {
      "command": "python",
      "args": ["core/server.py"],
      "transport": "stdio"
    }
  }
}
```

#### Claude Desktop Setup

Edit your Claude configuration:

```json
{
  "mcpServers": {
    "swaggermcp": {
      "command": "python",
      "args": ["/path/to/SwaggerMCP/core/server.py"],
      "transport": "stdio"
    }
  }
}
```

## 🛠️ Usage

### Via AI Assistant

Once connected, simply ask your AI assistant:

> "Convert this Python function to an API endpoint:"
> ```python
> def add(a: int, b: int) -> int:
>     return a + b
> ```

The AI will automatically:
1. Parse the function
2. Generate the API endpoint
3. Provide the Swagger UI link
4. Test the endpoint

### Via Direct API

```bash
# Upload Python file
curl -F "file=@functions.py" http://localhost:8000/upload

# Access Swagger UI
open http://localhost:8001/docs
```

## 📊 Generated Endpoints

SwaggerMCP supports various function types:

### 🔢 Mathematical Operations
```python
def add(a: int, b: int) -> int:
    return a + b

def factorial(n: int) -> int:
    return math.factorial(n)
```

### 📝 String Processing
```python
def is_palindrome(text: str) -> bool:
    return text.lower() == text.lower()[::-1]

def reverse_string(text: str) -> str:
    return text[::-1]
```

### 🧮 Algorithms
```python
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def binary_search(arr: list, target: int) -> int:
    # Implementation here
    pass
```

### 🔍 Data Analysis
```python
def analyze_text(text: str) -> dict:
    return {
        "length": len(text),
        "words": len(text.split()),
        "characters": len(text.replace(" ", ""))
    }
```

## 🌐 API Access

### Swagger UI
- **Main API**: http://localhost:8001/docs
- **OpenAPI Spec**: http://localhost:8001/openapi.json

### Example API Calls

```bash
# Test mathematical function
curl -X POST "http://localhost:8001/add" \
     -H "Content-Type: application/json" \
     -d '{"a": 5, "b": 3}'

# Test string function
curl -X POST "http://localhost:8001/is_palindrome" \
     -H "Content-Type: application/json" \
     -d '{"text": "racecar"}'
```

## 🔧 MCP Tools

Available tools for AI assistants:

| Tool | Description | Parameters |
|------|-------------|------------|
| `convert_python_to_api` | Convert Python code to API endpoints | `source_code`, `group` |
| `restart_server` | Restart the API server | `random_string` |
| `test_endpoints` | Test all available endpoints | `random_string` |
| `list_endpoints` | List current endpoints | None |
| `get_server_status` | Get server health status | None |

## 🚨 Security & Best Practices

### ⚠️ Security Considerations

1. **Code Execution**: SwaggerMCP executes uploaded Python code
2. **Development Use**: Designed for development and prototyping
3. **Production**: Add authentication, rate limiting, and sandboxing

### 🔒 Production Deployment

```bash
# Use Docker with security
docker run --security-opt seccomp=unconfined \
           --cap-drop=ALL \
           -p 8000:8000 \
           swaggermcp

# Add authentication
export API_KEY="your-secret-key"
python core/server.py --auth
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| MCP connection fails | Check Python path and restart client |
| Endpoints not appearing | Use `restart_server` tool |
| Port conflicts | Change ports in config or kill existing processes |
| Import errors | Ensure all dependencies are installed |

### Debug Mode

```bash
export DEBUG=1
python core/server.py --verbose
```

## 🔮 Roadmap

### 🎯 Upcoming Features
- [ ] **Type Safety** - Pydantic model generation
- [ ] **Authentication** - Built-in auth system
- [ ] **Rate Limiting** - API usage controls
- [ ] **Database Integration** - SQL/NoSQL support
- [ ] **Async Support** - Async function handling
- [ ] **Versioning** - API version management
- [ ] **Monitoring** - Usage analytics and logging

### 🚧 Current Limitations
- Single file uploads only
- No nested imports
- Basic type coercion
- Development-focused security

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/ibrahimsaleem/Swaggermcp.git
cd Swaggermcp

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black core/ utils/ examples/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. 📖 **Documentation**: Check the [docs/](docs/) folder
2. 🐛 **Issues**: Open an issue on GitHub
3. 💬 **Discussions**: Use GitHub Discussions
4. 📧 **Email**: Contact the maintainers

### Issue Template

When reporting issues, please include:
- Operating system and Python version
- MCP client being used
- Error messages and logs
- Steps to reproduce

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **MCP Protocol** - AI assistant integration
- **Swagger UI** - API documentation
- **Python AST** - Code parsing capabilities

---

<div align="center">

**Made with ❤️ for the AI community**

[![GitHub stars](https://img.shields.io/github/stars/ibrahimsaleem/Swaggermcp?style=social)](https://github.com/ibrahimsaleem/Swaggermcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ibrahimsaleem/Swaggermcp?style=social)](https://github.com/ibrahimsaleem/Swaggermcp/network/members)
[![GitHub issues](https://img.shields.io/github/issues/ibrahimsaleem/Swaggermcp)](https://github.com/ibrahimsaleem/Swaggermcp/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>