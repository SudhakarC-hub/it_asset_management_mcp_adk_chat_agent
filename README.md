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

**Option A: Terminal Chat (ADK CLI)**
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
adk run it_asset_manager_app
```

**Option B: Web Chat (Streamlit)**
```bash
cd /Users/sudhakarchigurupati/ADKProject/mcp_project
source venv/bin/activate
streamlit run streamlit_app/app.py
```
Opens in browser at http://localhost:8501

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

- [ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Tools Guide](https://google.github.io/adk-docs/tools-custom/mcp-tools/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Advanced: Using Multiple MCP Servers

ADK supports connecting to **multiple MCP servers** simultaneously, allowing you to build multi-service AI agents.

### Use Case

Imagine you have separate services for different domains:
- **IT Asset Management** (Port 8002)
- **HR Management** (Port 8003)
- **Finance** (Port 8004)

Each service has its own MCP server exposing domain-specific tools.

### Implementation

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


# MCP Server 1: IT Asset Management
asset_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8002/mcp"
    )
)

# MCP Server 2: HR Management
hr_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8003/mcp"
    )
)

# MCP Server 3: Finance
finance_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8004/mcp"
    )
)

# Create agent with ALL MCP toolsets
root_agent = Agent(
    model=LiteLlm(
        model="ollama_chat/mistral:latest",
        api_base="http://localhost:11434"
    ),
    name="multi_service_agent",
    description="Multi-service agent managing IT, HR, and Finance",
    instruction="""You are a multi-service assistant with access to:
    
    IT Asset Management:
    - list_assets, add_asset
    
    HR Management:
    - list_employees, add_employee, get_employee_details
    
    Finance:
    - list_invoices, create_invoice, get_budget
    
    Use the appropriate tools based on user requests.""",
    tools=[
        asset_mcp,    # All IT asset tools
        hr_mcp,       # All HR tools
        finance_mcp   # All finance tools
    ],
)
```

### Architecture

```
User: "List all assets and show me John's employee details"
    ↓
ADK Agent (Single LLM)
    ├─→ Asset MCP Server (Port 8002) → list_assets()
    └─→ HR MCP Server (Port 8003) → get_employee_details("John")
```

### Benefits

✅ **Separation of Concerns** - Each service has its own MCP server  
✅ **Independent Scaling** - Scale each service separately  
✅ **Team Ownership** - Different teams can own different MCP servers  
✅ **Easy Integration** - Just add another `McpToolset` to connect a new service  
✅ **Single Agent Interface** - Users interact with one agent that orchestrates all services

### How It Works

1. **Tool Discovery**: ADK automatically discovers all tools from all MCP servers
2. **LLM Decision**: The LLM analyzes the user request and decides which tools to use
3. **Parallel Execution**: ADK can call multiple tools from different MCP servers in parallel
4. **Response Synthesis**: The LLM combines results from multiple services into a coherent response

### Production Considerations

- **Service Discovery**: Use environment variables for MCP server URLs
- **Health Checks**: Implement health check endpoints for each MCP server
- **Error Handling**: Each MCP server should handle errors independently
- **Authentication**: Add authentication to MCP servers in production
- **Rate Limiting**: Implement rate limiting per MCP server
- **Monitoring**: Monitor each MCP server separately

### Example: Environment-Based Configuration

```python
import os

# Load MCP server URLs from environment
ASSET_MCP_URL = os.getenv("ASSET_MCP_URL", "http://localhost:8002/mcp")
HR_MCP_URL = os.getenv("HR_MCP_URL", "http://localhost:8003/mcp")
FINANCE_MCP_URL = os.getenv("FINANCE_MCP_URL", "http://localhost:8004/mcp")

# Create toolsets
asset_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=ASSET_MCP_URL)
)
hr_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=HR_MCP_URL)
)
finance_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=FINANCE_MCP_URL)
)

# Agent with all services
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral:latest"),
    tools=[asset_mcp, hr_mcp, finance_mcp],
)
```

This pattern allows you to build **enterprise-grade multi-service AI agents** that can orchestrate across your entire organization's services! 🚀
