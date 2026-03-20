"""AC control data endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import diagnostic_app
from .datatypes import DataItem, DataList, DataPayload

router = APIRouter()

@router.get("/data",
    response_model=DataList,
    summary="List data items",
    description="Returns all AC control data items including ID, name, category, and current values for monitoring temperature, humidity, fan speed, and climate zone settings",
    tags=["Data"]
)
def list_data():
    """List all data items"""
    return {"items": diagnostic_app.list_data_items()}

@router.get("/data/{item_id}",
    response_model=DataItem,
    summary="Get data item",
    description="Returns a specific AC control data item by ID with current values, category information, and associated groups for detailed climate monitoring",
    tags=["Data"]
)
def get_data_item(item_id: str = Path(..., description="The ID of the data item to retrieve")):
    """Get a specific data item by ID"""
    item = diagnostic_app.get_data_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Data item '{item_id}' not found")
    return item

@router.put("/data/{item_id}",
    response_model=DataItem,
    summary="Update data item",
    description="Updates fields of an AC control data item (partial update). Use this to modify temperature setpoints, fan speeds, or other configurable climate parameters",
    tags=["Data"]
)
def update_data_item(payload: DataPayload, item_id: str = Path(..., description="The ID of the data item to update")):
    """Update data item fields"""
    updated = diagnostic_app.update_data_item(item_id, payload.dict())
    if updated["status"] == "not found":
        raise HTTPException(status_code=404, detail=f"Data item '{item_id}' not found")
    return updated["item"]
