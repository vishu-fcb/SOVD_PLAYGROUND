"""AC control operations endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import diagnostic_app
from .datatypes import OperationList, OperationDescription, ExecutionRequest, ExecutionResult

router = APIRouter()

@router.get("/operations",
    response_model=OperationList,
    summary="List operations",
    description="Returns all available AC control operations such as set eco mode, adjust climate zones, defrost control, and other HVAC system functions",
    tags=["Operations"]
)
def list_operations():
    """List all available operations"""
    return {"operations": diagnostic_app.list_operations()}

@router.get("/operations/{operation_id}",
    response_model=OperationDescription,
    summary="Get operation description",
    description="Returns detailed AC control operation information including parameters, requirements, and supported modes without executing the operation",
    tags=["Operations"]
)
def get_operation_description(
    operation_id: str = Path(..., description="The ID of the operation to get description for", example="set_eco")
):
    """Get operation description without executing"""
    description = diagnostic_app.get_operation_description(operation_id)
    if not description:
        raise HTTPException(status_code=404, detail=f"Operation '{operation_id}' not found")
    return description

@router.post("/operations/{operation_id}/executions",
    response_model=ExecutionResult,
    summary="Execute operation",
    description="Execute an AC control operation (e.g., set eco mode, adjust temperature) with optional parameters and return execution status with result or error information",
    tags=["Operations"]
)
def execute_operation(
    operation_id: str = Path(..., description="The ID of the operation to execute", example="set_eco"),
    request: ExecutionRequest = ExecutionRequest()
):
    """Execute operation and return status"""
    execution = diagnostic_app.execute_operation(operation_id, request.parameters)

    # Return 200 with status (even for failures) as per SOVD spec
    return execution

@router.get("/operations/{operation_id}/executions/{execution_id}",
    response_model=ExecutionResult,
    summary="Get execution status",
    description="Returns execution status and result for a specific AC operation execution including completion state, result data, or error information if failed",
    tags=["Operations"]
)
def get_execution_status(
    operation_id: str = Path(..., description="The ID of the operation", example="set_eco"),
    execution_id: str = Path(..., description="The ID of the execution to check", example="12345-67890-abcdef")
):
    """Get execution status and result"""
    execution = diagnostic_app.get_execution_status(operation_id, execution_id)
    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found for operation '{operation_id}'"
        )
    return execution
