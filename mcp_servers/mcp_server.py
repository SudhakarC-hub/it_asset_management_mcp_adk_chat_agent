"""
MCP Server for IT Asset Management - Production Ready
Uses Streamable HTTP for scalability (Pattern 2 from ADK docs)
Runs on port 8002
"""

import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any
import httpx
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send
import mcp.types as types
import json
import uvicorn

logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8005"


def create_mcp_server():
    """Create and configure the MCP server"""
    app = Server("IT Asset Manager")
    
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available MCP tools"""
        return [
            types.Tool(
                name="list_assets",
                description="Retrieve all IT assets from the inventory",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
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
                            "description": "Name/model of the asset"
                        },
                        "owner": {
                            "type": "string",
                            "description": "Person who owns the asset"
                        },
                        "status": {
                            "type": "string",
                            "description": "Current status",
                            "default": "active"
                        }
                    },
                    "required": ["asset_id", "name", "owner"]
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """Handle tool calls from MCP clients"""
        
        if name == "list_assets":
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{API_BASE_URL}/assets")
                    response.raise_for_status()
                    assets = response.json()
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(assets, indent=2)
                    )]
                except httpx.HTTPError as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
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
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                except httpx.HTTPError as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    return app


def main(port: int = 8002, json_response: bool = False):
    """Main server function"""
    logging.basicConfig(level=logging.INFO)
    
    mcp_server = create_mcp_server()
    
    # Create session manager with stateless mode for scalability
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=json_response,
        stateless=True,  # Important for production scalability
    )
    
    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)
    
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Manage session manager lifecycle"""
        async with session_manager.run():
            logger.info("MCP Streamable HTTP server started!")
            logger.info(f"Connecting to API Server at {API_BASE_URL}")
            logger.info(f"MCP endpoint: http://0.0.0.0:{port}/mcp")
            try:
                yield
            finally:
                logger.info("MCP server shutting down...")
    
    # Create ASGI application
    starlette_app = Starlette(
        debug=False,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )
    
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    print("Starting Production-Ready MCP Server")
    print("Using Streamable HTTP (Pattern 2 from ADK docs)")
    main()
