from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams


# Initialize MCP toolset to connect to IT Asset Management MCP server via SSE
mcp_connection = SseConnectionParams(
    url="http://localhost:8002/sse"
)

mcp_toolset = McpToolset(
    connection_params=mcp_connection
)

# Create IT Asset Management Agent
root_agent = Agent(
    name="it_asset_manager_agent",
    model=LiteLlm(model="ollama_chat/mistral:latest"),
    description=(
        "Agent that manages IT assets using MCP tools."
    ),
    instruction=(
        "You are an IT Asset Management assistant. "
        "You can help users list all IT assets and add new assets to the inventory. "
        "When users ask to list assets or show inventory, use the list_assets tool. "
        "When users ask to add an asset, use the add_asset tool with the provided details. "
        "Be helpful and concise in your responses. "
        "Format asset lists in a clear, readable way."
    ),
    tools=[mcp_toolset],
)