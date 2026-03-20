"""AC control fault management endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import diagnostic_app
from .datatypes import FaultList, Fault, StatusResponse

router = APIRouter()

@router.get("/faults",
    response_model=FaultList,
    summary="List faults",
    description="Returns all stored faults (DTCs) for AC control system including error codes, severity levels, and status information for climate system diagnostics",
    tags=["Faults"]
)
def list_faults():
    """List all stored faults (DTCs)"""
    return {"items": diagnostic_app.get_faults()}

@router.get("/faults/{code}",
    response_model=Fault,
    summary="Get fault details",
    description="Returns detailed fault information by code including environment data, severity level, and diagnostic translation IDs for HVAC system repair procedures",
    tags=["Faults"]
)
def get_fault(code: str = Path(..., description="The fault code to retrieve")):
    """Get fault details by code"""
    fault = diagnostic_app.get_fault(code)
    if not fault:
        raise HTTPException(status_code=404, detail=f"Fault '{code}' not found")
    return fault

@router.delete("/faults",
    response_model=StatusResponse,
    summary="Clear all faults",
    description="Clears all stored faults from AC control system memory. Use with caution as this removes all climate system diagnostic trouble codes",
    tags=["Faults"]
)
def clear_faults():
    """Clear all faults"""
    diagnostic_app.clear_faults()
    return {"status": "all faults cleared"}

@router.delete("/faults/{code}",
    response_model=Fault,
    summary="Delete fault",
    description="Deletes a specific fault by code from the AC control system memory. Returns the deleted fault details for confirmation",
    tags=["Faults"]
)
def delete_fault(code: str = Path(..., description="The fault code to delete")):
    """Delete a specific fault by code"""
    fault = diagnostic_app.get_fault(code)
    if not fault:
        raise HTTPException(status_code=404, detail=f"Fault '{code}' not found")
    
    diagnostic_app.faults.remove(fault)
    return fault
