from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="IT Asset Manager API")

# 1. The Data Model
class Asset(BaseModel):
    id: int
    name: str
    owner: str
    status: str = "active"

# 2. In-Memory Database
assets_db: List[Asset] = [
    Asset(id=1, name="MacBook Pro 16", owner="Alice", status="active"),
    Asset(id=2, name="Dell XPS 13", owner="Bob", status="maintenance")
]

# 3. Endpoints

@app.get("/assets", response_model=List[Asset])
def get_assets():
    """
    Retrieve a list of all IT assets.
    """
    return assets_db

@app.post("/assets", response_model=Asset)
def create_asset(asset: Asset):
    """
    Add a new asset to the inventory.
    """
    assets_db.append(asset)
    return asset

if __name__ == "__main__":
    import uvicorn
    # Run with: python asset_manager.py
    uvicorn.run(app, host="0.0.0.0", port=8005)