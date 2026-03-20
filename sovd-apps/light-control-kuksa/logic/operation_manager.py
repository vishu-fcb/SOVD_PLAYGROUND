"""
Operation execution and management system.
"""

import inspect
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone
from .light_operations import LightOperations


class OperationManager:
    """Manages SOVD operations and their execution."""

    def __init__(self, light_operations: LightOperations):
        self.light_operations = light_operations
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.logs = []  # Reference to main logs will be set by parent

    def set_logger(self, add_log_func: Callable[[str], None]):
        """Set the logging function from the main data manager."""
        self.add_log = add_log_func

    def get_operation_description(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation description without executing."""
        if hasattr(self.light_operations, operation_id):
            func = getattr(self.light_operations, operation_id)

            description = {
                "id": operation_id,
                "name": operation_id.replace("_", " ").title(),
                "description": func.__doc__ or f"Execute {operation_id} operation",
                "parameters": [],
                "proximity_requirements": [],
                "supported_modes": ["normal"]
            }
            return description
        return None

    async def execute_operation(self, operation_id: str, parameters: Optional[Dict[str, Any]] = None) -> dict:
        """Execute an operation and return execution info."""
        execution_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Check if operation exists
        if not hasattr(self.light_operations, operation_id):
            return {
                "id": execution_id,
                "status": "failed",
                "error": f"Unknown operation '{operation_id}'",
                "created_at": timestamp,
                "completed_at": timestamp
            }

        # Create execution record
        execution_record = {
            "id": execution_id,
            "operation_id": operation_id,
            "status": "running",
            "created_at": timestamp,
            "parameters": parameters or {}
        }
        self.executions[execution_id] = execution_record

        try:
            # Execute the operation
            func = getattr(self.light_operations, operation_id)
            if inspect.iscoroutinefunction(func):
                if parameters:
                    result = await func(**parameters)
                else:
                    result = await func()
            else:
                if parameters:
                    result = func(**parameters)
                else:
                    result = func()

            # Update execution record
            execution_record.update({
                "status": "completed",
                "result": result,
                "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })

            if hasattr(self, 'add_log'):
                self.add_log(f"Operation {operation_id} completed successfully")

            return execution_record

        except Exception as e:
            # Update execution record with error
            execution_record.update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })

            if hasattr(self, 'add_log'):
                self.add_log(f"Operation {operation_id} failed: {str(e)}")

            return execution_record

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific execution."""
        return self.executions.get(execution_id)

    def list_executions(self) -> Dict[str, Dict[str, Any]]:
        """List all executions."""
        return self.executions

    # Map operation IDs to light operation methods
    def get_available_operations(self) -> list:
        """Get list of available operation IDs."""
        operations = []
        for attr_name in dir(self.light_operations):
            if attr_name.startswith('toggle_') or attr_name.startswith('set_'):
                # Convert method name to operation ID
                operation_id = attr_name
                operations.append(operation_id)
        return operations
