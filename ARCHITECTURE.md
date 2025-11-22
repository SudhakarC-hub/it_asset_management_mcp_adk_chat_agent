# IT Asset Manager - Project Structure

## Clean Project Structure

```
mcp_project/
│
├── swagger_api/              # Backend API
│   └── api_server.py        # FastAPI server (Port 8005)
│
├── mcp_servers/              # MCP Protocol Layer
│   └── mcp_server.py        # MCP server with Streamable HTTP (Port 8002)
│
├── it_asset_manager_app/     # ADK Agent (Created with `adk create`)
│   ├── agent.py             # Agent definition with MCP toolset
│   ├── __init__.py          # Package init
│   └── .env                 # Environment variables
│
├── venv/                     # Python virtual environment
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Input: "List all assets"                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ADK Agent (it_asset_manager_app/agent.py)                  │
│  - LLM: Ollama Mistral (localhost:11434)                    │
│  - Decides to use list_assets tool                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  McpToolset (google.adk.tools.mcp_tool)                     │
│  - Connection: StreamableHTTPConnectionParams               │
│  - URL: http://localhost:8002/mcp                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP POST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP Server (mcp_servers/mcp_server.py)                     │
│  - Receives tool call: list_assets                          │
│  - Uses StreamableHTTPSessionManager                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP GET
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend (swagger_api/api_server.py)                │
│  - Endpoint: GET /assets                                    │
│  - Returns: JSON list of assets                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Response flows back up
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  User sees: Formatted list of IT assets                     │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. ADK (Agent Development Kit)
- Google's framework for building AI agents
- Handles LLM orchestration, tool calling, session management
- Our agent uses `LlmAgent` with Ollama Mistral

### 2. MCP (Model Context Protocol)
- Open standard for LLM-tool communication
- Defines how tools are discovered and called
- Our implementation uses Streamable HTTP transport

### 3. McpToolset
- ADK's integration with MCP
- Automatically discovers tools from MCP server
- Proxies tool calls between agent and MCP server

### 4. Streamable HTTP
- Production-ready MCP transport pattern
- Stateless, scalable, HTTP-based
- Better than STDIO for deployed services

## Code Walkthrough

### Agent (`it_asset_manager_app/agent.py`)
```python
# 1. Connect to MCP server
mcp_connection = StreamableHTTPConnectionParams(
    url="http://localhost:8002/mcp"
)

# 2. Create toolset
mcp_toolset = McpToolset(connection_params=mcp_connection)

# 3. Create agent with toolset
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral:latest"),
    tools=[mcp_toolset],  # MCP tools available to agent
)
```

### MCP Server (`mcp_servers/mcp_server.py`)
```python
# 1. Define tools
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [Tool(name="list_assets", ...)]

# 2. Handle tool calls
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "list_assets":
        # Call FastAPI
        response = await client.get(f"{API_BASE_URL}/assets")
        return [TextContent(text=json.dumps(response.json()))]

# 3. Expose via Streamable HTTP
session_manager = StreamableHTTPSessionManager(app=mcp_server, stateless=True)
```

### FastAPI (`swagger_api/api_server.py`)
```python
# Simple REST API
@app.get("/assets")
async def list_assets():
    return assets_db

@app.post("/assets")
async def add_asset(asset: Asset):
    assets_db.append(asset)
    return asset
```

## Why This Architecture?

1. **Separation of Concerns**
   - FastAPI: Data management
   - MCP Server: Protocol translation
   - ADK Agent: AI orchestration

2. **Scalability**
   - Each component can scale independently
   - Streamable HTTP is stateless
   - Can deploy to Cloud Run, Kubernetes, etc.

3. **Flexibility**
   - Easy to add more tools to MCP server
   - Can swap FastAPI for any backend
   - Agent can use multiple MCP servers

4. **Production Ready**
   - Follows ADK best practices (Pattern 2)
   - Proper error handling
   - Stateless design for horizontal scaling
