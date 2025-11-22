# IT Asset Manager - ADK + MCP POC

A production-ready IT Asset Management system demonstrating **Google ADK** integration with **Model Context Protocol (MCP)** using **Streamable HTTP** (Pattern 2).

## Architecture

```
User (Terminal)
    ↓
ADK Agent (Ollama Mistral)
    ↓
MCP Toolset (Streamable HTTP)
    ↓
MCP Server (Port 8002)
    ↓
FastAPI Backend (Port 8005)
```

## Components

### 1. FastAPI Backend (`swagger_api/api_server.py`)
- REST API for IT asset management
- Endpoints: GET/POST `/assets`
- Port: **8005**

### 2. MCP Server (`mcp_servers/mcp_server.py`)
- Exposes FastAPI as MCP tools using **Streamable HTTP** (production pattern)
- Tools: `list_assets`, `add_asset`
- Port: **8002**
- Endpoint: `/mcp`

### 3. ADK Agent (`it_asset_manager_app/agent.py`)
- Google ADK agent with Ollama Mistral LLM
- Uses `McpToolset` with `StreamableHTTPConnectionParams`
- Connects to MCP server for tool execution

## Setup

### Prerequisites
- Python 3.11+
- Ollama with Mistral model
- Virtual environment

### Installation

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure Ollama is running
ollama run mistral
```

## Running the System

Open **3 separate terminals**:

### Terminal 1: FastAPI Server
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
python swagger_api/api_server.py
```
✅ Running on: http://localhost:8005

### Terminal 2: MCP Server
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
python mcp_servers/mcp_server.py
```
✅ Running on: http://localhost:8002/mcp

### Terminal 3: ADK Agent
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
adk run it_asset_manager_app
```

## Usage

Once the ADK agent is running, try these commands:

```
You: hello
You: List all assets
You: Add asset id 10, name Surface Pro, owner Mike, status active
You: Show me the inventory
```

## Key Files

```
mcp_project/
├── swagger_api/
│   └── api_server.py          # FastAPI backend
├── mcp_servers/
│   └── mcp_server.py          # MCP server (Streamable HTTP)
├── it_asset_manager_app/
│   ├── agent.py               # ADK agent with MCP toolset
│   ├── __init__.py
│   └── .env                   # Environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## How It Works

1. **User Input** → ADK agent receives user message
2. **LLM Decision** → Ollama Mistral decides which tool to use
3. **MCP Call** → ADK's `McpToolset` calls MCP server via Streamable HTTP
4. **Tool Execution** → MCP server executes tool (calls FastAPI)
5. **Response** → Result flows back through the chain to user

## MCP Tools Available

### `list_assets()`
Retrieves all IT assets from the inventory.

**Example**: "List all assets"

### `add_asset(asset_id, name, owner, status)`
Adds a new IT asset to the inventory.

**Parameters**:
- `asset_id` (int): Unique identifier
- `name` (str): Asset name/model
- `owner` (str): Person assigned to asset
- `status` (str): Status (default: "active")

**Example**: "Add asset id 5, name iPad Pro, owner Sarah, status active"

## Production Pattern

This implementation uses **Pattern 2: Remote MCP Servers (Streamable HTTP)** from the [ADK MCP documentation](https://google.github.io/adk-docs/tools-custom/mcp-tools/), which is recommended for production deployments due to:

- ✅ Scalability (stateless mode)
- ✅ HTTP-based communication
- ✅ Suitable for Cloud Run / containerized deployments
- ✅ Better error handling and monitoring

## Verification

### Test FastAPI
```bash
curl http://localhost:8005/assets
```

### Test MCP Server
The MCP server should show connection logs when the agent connects.

### Test Agent
The agent should respond to greetings and execute MCP tools when asked.

## Troubleshooting

### Agent not responding
- Check Ollama is running: `ollama list`
- Verify MCP server is running on port 8002
- Check FastAPI is running on port 8005

### Port conflicts
```bash
# Check ports
lsof -i :8005  # FastAPI
lsof -i :8002  # MCP
lsof -i :11434 # Ollama

# Kill if needed
lsof -ti:8002 | xargs kill -9
```

### Import errors
Make sure you're in the project root when running `adk run`.

## Technology Stack

- **Google ADK**: Agent framework
- **MCP (Model Context Protocol)**: Tool integration protocol
- **FastAPI**: Backend API
- **Ollama**: Local LLM (Mistral)
- **Streamable HTTP**: Production-ready MCP transport
- **Python 3.11**: Runtime

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Tools Guide](https://google.github.io/adk-docs/tools-custom/mcp-tools/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
