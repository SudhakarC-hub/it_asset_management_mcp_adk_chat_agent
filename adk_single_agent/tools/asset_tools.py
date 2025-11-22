"""
Custom tools for IT Asset Management
These tools directly call the FastAPI server endpoints
"""

import httpx
from google.adk.tools import FunctionTool
from typing import List, Dict, Any


async def list_assets() -> List[Dict[str, Any]]:
    """
    Retrieve all IT assets from the inventory.
    
    Returns:
        List of assets with their id, name, owner, and status
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8005/assets")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return [{"error": f"Failed to retrieve assets: {str(e)}"}]


async def add_asset(
    asset_id: int,
    name: str,
    owner: str,
    status: str = "active"
) -> Dict[str, Any]:
    """
    Add a new IT asset to the inventory.
    
    Args:
        asset_id: Unique identifier for the asset
        name: Name/model of the asset (e.g., "MacBook Pro 16")
        owner: Person who owns/is assigned the asset
        status: Current status of the asset (default: "active")
    
    Returns:
        The created asset object
    """
    asset_data = {
        "id": asset_id,
        "name": name,
        "owner": owner,
        "status": status
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8005/assets",
                json=asset_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Failed to add asset: {str(e)}"}


# Create ADK FunctionTools
list_assets_tool = FunctionTool(func=list_assets)
add_asset_tool = FunctionTool(func=add_asset)
