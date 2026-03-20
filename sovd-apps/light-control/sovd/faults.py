"""Light control fault management endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import lightctrl
from .datatypes import FaultList, Fault, StatusResponse

router = APIRouter()

@router.get("/faults",
    response_model=FaultList,
    summary="List faults",
    description="Returns all stored faults (DTCs) for light control system including error codes, severity levels, and status information",
    tags=["Faults"]
)
def list_faults():
    """List all stored faults (DTCs)"""
    return {"items": lightctrl.get_faults()}

@router.get("/faults/{code}",
    response_model=Fault,
    summary="Get fault details",
    description="Returns detailed fault information by code including environment data, severity level, and diagnostic translation IDs for repair procedures",
    tags=["Faults"]
)
def get_fault(code: str = Path(..., description="The fault code to retrieve")):
    """Get fault details by code"""
    fault = lightctrl.get_fault(code)
    if not fault:
        raise HTTPException(status_code=404, detail=f"Fault '{code}' not found")
    return fault

@router.delete("/faults",
    response_model=StatusResponse,
    summary="Clear all faults",
    description="Clears all stored faults from light control system memory. Use with caution as this removes all diagnostic trouble codes",
    tags=["Faults"]
)
def clear_faults():
    """Clear all faults"""
    lightctrl.clear_faults()
    return {"status": "all faults cleared"}

@router.delete("/faults/{code}",
    response_model=Fault,
    summary="Delete fault",
    description="Deletes a specific fault by code from the light control system memory. Returns the deleted fault details for confirmation",
    tags=["Faults"]
)
def delete_fault(code: str = Path(..., description="The fault code to delete")):
    """Delete a specific fault by code"""
    result = lightctrl.delete_fault(code)
    if result["status"] == "not found":
        raise HTTPException(status_code=404, detail=f"Fault '{code}' not found")
    return result
