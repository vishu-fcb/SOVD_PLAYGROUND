"""Light control data endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import lightctrl
from .datatypes import DataItem, DataList, DataPayload

router = APIRouter()

@router.get("/data",
    response_model=DataList,
    summary="List data items",
    description="Returns all light control data items including ID, name, category, and current values for monitoring beam status, brightness levels, and light states",
    tags=["Data"]
)
def list_data():
    """List all data items"""
    return {"items": lightctrl.list_data_items()}

@router.get("/data/{item_id}",
    response_model=DataItem,
    summary="Get data item",
    description="Returns a specific light control data item by ID with current values, category information, and associated groups for detailed monitoring",
    tags=["Data"]
)
def get_data_item(item_id: str = Path(..., description="The ID of the data item to retrieve")):
    """Get a specific data item by ID"""
    item = lightctrl.get_data_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Data item '{item_id}' not found")
    return item

@router.put("/data/{item_id}",
    response_model=DataItem,
    summary="Update data item",
    description="Updates fields of a light control data item (partial update). Use this to modify brightness values or other configurable parameters",
    tags=["Data"]
)
def update_data_item(payload: DataPayload, item_id: str = Path(..., description="The ID of the data item to update")):
    """Update data item fields"""
    updated = lightctrl.update_data_item(item_id, payload.dict())
    if updated["status"] == "not found":
        raise HTTPException(status_code=404, detail=f"Data item '{item_id}' not found")
    return updated["item"]
