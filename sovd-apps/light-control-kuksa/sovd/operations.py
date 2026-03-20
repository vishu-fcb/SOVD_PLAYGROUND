"""Light control operations endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import lightctrl
from .datatypes import OperationList, OperationDescription, ExecutionRequest, ExecutionResult

router = APIRouter()

@router.get("/operations",
    response_model=OperationList,
    summary="List operations",
    description="Returns all available light control operations",
    tags=["Operations"]
)
def list_operations():
    """List all available operations"""
    return {"operations": lightctrl.get_all_operations_descriptions()}

@router.get("/operations/{operation_id}",
    response_model=OperationDescription,
    summary="Get operation description",
    description="Returns light control operation details without executing it",
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
    description="Execute predefined light control operation to perform actions like turning all lights on/off in one go. Provide operation parameters as needed and receive execution status",
    tags=["Operations"]
)
async def execute_operation(
    operation_id: str = Path(..., description="The ID of the operation to execute", example="toggle_beam"),
    request: ExecutionRequest = ExecutionRequest()
):
    """Execute operation and return status"""
    execution = await lightctrl.execute_operation(operation_id, request.parameters)

    # Return 200 with status (even for failures) as per SOVD spec
    return execution

@router.get("/operations/{operation_id}/executions/{execution_id}",
    response_model=ExecutionResult,
    summary="Get execution status",
    description="Returns execution status and result for a specific light control operation execution",
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
