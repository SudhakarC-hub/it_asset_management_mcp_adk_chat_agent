# IT Asset Manager with MCP Integration

A complete IT Asset Management system with FastAPI backend, MCP server, Google ADK agent, and Streamlit chat interface.

## Architecture

- **FastAPI Server** (Port 8005): REST API for IT asset management
- **MCP Server** (Port 8002): Exposes API as MCP tools via HTTP SSE
- **Ollama Mistral** (Port 11434): Local LLM for agent intelligence
- **Streamlit Chat** (Port 8501+): User-friendly chat interface

## Setup

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Ollama (if not running)
```bash
ollama run mistral
```

## Running the Application

Open **4 separate terminals** and run each command:

### Terminal 1: FastAPI Server
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
python swagger_api/api_server.py
```
Server runs on: **http://localhost:8005**  
Swagger UI: **http://localhost:8005/docs**

### Terminal 2: MCP Server
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
python mcp_servers/mcp_server.py
```
Server runs on: **http://localhost:8002**

### Terminal 3: Ollama Mistral
```bash
ollama run mistral
```
Server runs on: **http://localhost:11434**

### Terminal 4: Streamlit Chat App
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
streamlit run front_end/app.py
```
Chat interface: **http://localhost:8501** (or next available port)

## Usage

Open the Streamlit chat interface and try:

- **"List all assets"** - Shows all IT assets
- **"Show me the inventory"** - Lists assets
- **"Add asset id 4, name M5 Pro, owner Sudha, status active"** - Adds new asset

## MCP Tools Available

1. **list_assets()** - Retrieve all IT assets
2. **add_asset(asset_id, name, owner, status)** - Add new asset

## Deactivate Virtual Environment
```bash
deactivate
```

---

## Troubleshooting

### Python Version Compatibility

**Issue**: `fastmcp` and `mcp` packages require Python 3.10+

**Solution**: 
```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Recreate virtual environment with Python 3.11
rm -rf venv
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency Conflicts

**Issue**: Conflicts between `fastapi`, `google-adk`, and `streamlit` versions

**Solutions**:
1. **FastAPI/ADK conflict** (anyio version mismatch):
   - Updated `fastapi>=0.115.0` and `uvicorn>=0.32.0` in requirements.txt
   
2. **ADK/Streamlit conflict** (tenacity version mismatch):
   - Updated `streamlit>=1.40.0` in requirements.txt

### ADK Session Management Issues

**Issue**: `ValueError: Session not found: session_1` when using ADK Runner

**Root Cause**: Complex session management with `Runner` and `InMemorySessionService` in Streamlit environment

**Solution**: Simplified implementation bypassing ADK Runner:
- Direct API calls to FastAPI endpoints instead of going through full ADK/MCP chain
- Simple intent detection for "list" vs "add" commands
- Ollama integration for general conversation

**Files Modified**:
- `front_end/app.py` - Uses direct `httpx` calls instead of ADK Runner
- Maintains MCP server infrastructure (still running and available)

### MCP Server Configuration

**Issue**: MCP server needs to use SSE transport, not STDIO

**Solution**: Updated `mcp_servers/mcp_server.py`:
```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette

# Create Starlette app for SSE
app = Starlette(routes=[Route("/sse", endpoint=handle_sse)])
uvicorn.run(app, host="0.0.0.0", port=8002)
```

### Agent Import Issues

**Issue**: `from google.adk.agents import Agent` causes app_name mismatch

**Solution**: Use specific import:
```python
from google.adk.agents.llm_agent import Agent
```

### Virtual Environment Location

**Issue**: Multiple virtual environments in different folders

**Solution**: Single venv at project root:
```bash
# Remove old venvs
rm -rf swagger_api/venv

# Create at project root
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
python3.11 -m venv venv
```

### Port Conflicts

**Ports Used**:
- 8005: FastAPI Server
- 8002: MCP Server  
- 11434: Ollama
- 8501+: Streamlit (auto-increments if port busy)

**Check if port is in use**:
```bash
lsof -i :8005
lsof -i :8002
```

### Asset Parsing Issues

**Issue**: "Add asset" command not parsing correctly

**Solution**: Use regex patterns to extract structured data:
```python
# Extract id, name, owner, status from natural language
id_match = re.search(r'id["\s:]*(\d+)', prompt_lower)
name_match = re.search(r'name["\s:]*["\'​]?([^,"\'​]+)["\'​]?', prompt)
owner_match = re.search(r'owner["\s:]*["\'​]?([^,"\'​]+)["\'​]?', prompt)
status_match = re.search(r'status["\s:]*["\'​]?([^,"\'​]+)["\'​]?', prompt)
```

### Common Error Messages

1. **"ModuleNotFoundError: No module named 'fastapi'"**
   - Run: `pip install -r requirements.txt`

2. **"Session not found"**
   - Use simplified app.py without ADK Runner

3. **"App name mismatch"**
   - Use `from google.adk.agents.llm_agent import Agent`

4. **"Could not find a version that satisfies the requirement"**
   - Upgrade Python to 3.10+ and recreate venv

### Verification Steps

After setup, verify each component:

1. **FastAPI**: Visit http://localhost:8005/docs
2. **MCP Server**: Should show "Starting MCP Server" message
3. **Ollama**: Run `ollama list` to see installed models
4. **Streamlit**: Should open browser automatically

### Future Improvements

For full ADK/MCP integration (currently simplified):
- Investigate ADK session creation in Streamlit context
- Test with `adk run` CLI instead of custom Runner
- Use ADK's built-in session management patterns
- Implement proper tool calling via MCP protocol

