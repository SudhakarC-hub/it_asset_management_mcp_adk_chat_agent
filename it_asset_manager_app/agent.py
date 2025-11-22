"""
IT Asset Management Agent with MCP Integration
Created using: adk create it_asset_manager_app
Uses Streamable HTTP (Production Pattern 2 from ADK docs)
"""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


# Initialize MCP toolset using Streamable HTTP (production pattern)
mcp_connection = StreamableHTTPConnectionParams(
    url="http://localhost:8002/mcp"
)

mcp_toolset = McpToolset(
    connection_params=mcp_connection
)

# Create IT Asset Management Agent
root_agent = Agent(
    model=LiteLlm(
        model="ollama_chat/mistral:latest",
        api_base="http://localhost:11434"
    ),
    name="it_asset_manager",
    description="Agent that manages IT assets using MCP tools.",
    instruction="""You are an IT Asset Management assistant with access to MCP tools.

Available Tools:
- list_assets: Retrieve all IT assets from the inventory
- add_asset: Add a new IT asset to the inventory

Instructions:
1. When users ask to list, show, or display assets, use the list_assets tool
2. When users ask to add or create an asset, use the add_asset tool with the provided details
3. Be helpful and concise in your responses
4. Format asset lists in a clear, readable way with proper formatting
5. Always confirm successful operations

Example interactions:
- "List all assets" → Use list_assets tool
- "Add asset id 5, name iPad Pro, owner Sarah" → Use add_asset tool
- "Show me the inventory" → Use list_assets tool
""",
    tools=[mcp_toolset],
)
