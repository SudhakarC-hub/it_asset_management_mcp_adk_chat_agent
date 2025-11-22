"""
MCP Server for IT Asset Management
Exposes API endpoints from http://localhost:8005 as MCP tools
Runs on port 8002 using HTTP SSE protocol
"""

import asyncio
import httpx
from typing import List, Dict, Any
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.types import Tool, TextContent
import json
import uvicorn


# Initialize MCP server
mcp_server = Server("IT Asset Manager")

# API base URL
API_BASE_URL = "http://localhost:8005"


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_assets",
            description="Retrieve all IT assets from the inventory",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="add_asset",
            description="Add a new IT asset to the inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "integer",
                        "description": "Unique identifier for the asset"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name/model of the asset (e.g., 'MacBook Pro 16')"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Person who owns/is assigned the asset"
                    },
                    "status": {
                        "type": "string",
                        "description": "Current status of the asset",
                        "default": "active"
                    }
                },
                "required": ["asset_id", "name", "owner"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "list_assets":
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_BASE_URL}/assets")
                response.raise_for_status()
                assets = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(assets, indent=2)
                )]
            except httpx.HTTPError as e:
                return [TextContent(
                    type="text",
                    text=f"Error: Failed to retrieve assets: {str(e)}"
                )]
    
    elif name == "add_asset":
        asset_data = {
            "id": arguments.get("asset_id"),
            "name": arguments.get("name"),
            "owner": arguments.get("owner"),
            "status": arguments.get("status", "active")
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{API_BASE_URL}/assets",
                    json=asset_data
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except httpx.HTTPError as e:
                return [TextContent(
                    type="text",
                    text=f"Error: Failed to add asset: {str(e)}"
                )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]


# SSE endpoint handler
async def handle_sse(request):
    """Handle SSE connections"""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


# Create Starlette app for SSE
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
    ]
)


if __name__ == "__main__":
    print("Starting MCP Server on http://0.0.0.0:8002")
    print(f"Connecting to API Server at {API_BASE_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8002)
