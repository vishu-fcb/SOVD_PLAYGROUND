"""Light control operations endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import lightctrl
from .datatypes import OperationList, OperationDescription, ExecutionRequest, ExecutionResult

router = APIRouter()

@router.get("/operations",
    response_model=OperationList,
    summary="List operations",
    description="Returns all available light control operations such as toggle beam, adjust brightness, enable/disable auto mode, and other control functions",
    tags=["Operations"]
)
def list_operations():
    """List all available operations"""
    return {"operations": lightctrl.list_operations()}

@router.get("/operations/{operation_id}",
    response_model=OperationDescription,
    summary="Get operation description",
    description="Returns detailed light control operation information including parameters, requirements, and supported modes without executing the operation",
    tags=["Operations"]
)
def get_operation_description(
    operation_id: str = Path(..., description="The ID of the operation to get description for", example="toggle_beam")
):
    """Get operation description without executing"""
    description = lightctrl.get_operation_description(operation_id)
    if not description:
        raise HTTPException(status_code=404, detail=f"Operation '{operation_id}' not found")
    return description

@router.post("/operations/{operation_id}/executions",
    response_model=ExecutionResult,
    summary="Execute operation",
    description="Execute a light control operation (e.g., toggle beam, adjust brightness) with optional parameters and return execution status with result or error information",
    tags=["Operations"]
)
def execute_operation(
    operation_id: str = Path(..., description="The ID of the operation to execute", example="toggle_beam"),
    request: ExecutionRequest = ExecutionRequest()
):
    """Execute operation and return status"""
    execution = lightctrl.execute_operation(operation_id, request.parameters)

    # Return 200 with status (even for failures) as per SOVD spec
    return execution

@router.get("/operations/{operation_id}/executions/{execution_id}",
    response_model=ExecutionResult,
    summary="Get execution status",
    description="Returns execution status and result for a specific light control operation execution including completion state, result data, or error information if failed",
    tags=["Operations"]
)
def get_execution_status(
    operation_id: str = Path(..., description="The ID of the operation", example="toggle_beam"),
    execution_id: str = Path(..., description="The ID of the execution to check", example="12345-67890-abcdef")
):
    """Get execution status and result"""
    execution = lightctrl.get_execution_status(operation_id, execution_id)
    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found for operation '{operation_id}'"
        )
    return execution
