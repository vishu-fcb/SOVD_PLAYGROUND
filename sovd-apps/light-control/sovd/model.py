import inspect
import uuid

from typing import List, Dict, Any, Optional
from .datatypes import DataItem, DataCategory
from settings import settings
from datetime import datetime, timezone

# Import modular logic components
from logic.operation_manager import OperationManager
from logic.light_config import LightDataConfig


class LightControl:
    """SOVD Light Control app for managing vehicle light signals."""

    def __init__(self, app_id: str, name: str, version: str, vendor: str, description: str):
        # Metadata
        self.id = app_id
        self.name = name
        self.version = version
        self.vendor = vendor
        self.description = description

        # Core resources
        self.config: Dict[str, Any] = {}
        self.data: List[Dict[str, Any]] = []
        self.faults: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self.operations: List[Dict[str, Any]] = []
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.supported_data_categories: List[str] = []

        # Initialize modular logic components
        self.operation_manager = OperationManager()

        # Convert basic light data to SOVD DataItems for compatibility
        self.light_data: dict = {}
        for light_key, light_config in LightDataConfig.LIGHT_DATA_BASIC.items():
            self.light_data[light_key] = DataItem(
                id=light_config["description"].replace(" ", ""),
                name=light_config["description"],
                category=DataCategory.CURRENT_DATA,
                groups=[light_config["type"]],
                data={"state": None}
            )

        self._read_in_lights()
        self._init_light_ctrl_data()

        self.add_log("light-control started")

    def _read_in_lights(self):
        # Read current light status to set initial state
        for light, value in self.light_data.items():
            state = None
            value.data = {"state" : state}

        self.add_log("read in lights")

    def _init_light_ctrl_data(self):
        for light, value in self.light_data.items():
            self.add_data_item({
                "id": value.id,
                "name": value.name,
                "category": value.category,
                "groups": value.groups,
                "data": value.data,  # Wert aus Attribut lesen
            })

        self.add_data_item({
            "id": "AppInfo",
            "name": "Light Control Version",
            "category": "identData",
            "data": {"Version": self.version}
        })

    # CONFIG
    def get_configurations(self) -> Dict[str, Any]:
        return self.config

    def set_config(self, key: str, value: Any):
        self.config[key] = value
        self.add_log(f"{key} was set to {value}")

    # DATA
    def add_data_item(self, item: Dict[str, Any]):
        self.data.append(item)

    def list_data_items(self) -> List[Dict[str, Any]]:
        return self.data

    def get_data_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        # read in data from light
        # when it is returned update the class
        # return the read in value
        return next((d for d in self.data if d.get("id") == item_id), None)

    def update_data_item(self, item_id: str, new_data: dict) -> dict:
        """
        Safely update only existing keys of a data item.
        - Does not add new keys
        - Does not delete existing keys
        """
        item = self.get_data_item(item_id)
        if not item:
            return {"status": "not found"}

        updated_fields = []
        if "data" in new_data and isinstance(new_data["data"], dict):
            for key, value in new_data["data"].items():
                if key in item["data"]:
                    item["data"][key] = value
                    updated_fields.append(key)

        #set the value at the sensor

        if updated_fields:
            self.add_log(f"{updated_fields} was set to {item}")
            return {"status": "updated", "updated_fields": updated_fields, "item": item}
        else:
            return {"status": "nothing to update"}

    # FAULTS
    def add_fault(self, fault: Dict[str, Any]):
        self.faults.append(fault)

    def get_faults(self) -> List[Dict[str, Any]]:
        return self.faults

    def get_fault(self, code: str) -> Optional[Dict[str, Any]]:
        return next((f for f in self.faults if f.get("code") == code), None)

    def delete_fault(self, code: str) -> Dict[str, Any]:
        """Delete a fault by code."""
        original_len = len(self.faults)
        self.faults = [f for f in self.faults if f.get("code") != code]
        if len(self.faults) < original_len:
            return {"status": "deleted"}
        return {"status": "not found"}

    def clear_faults(self):
        self.faults.clear()

    # LOGS
    def add_log(self, event: str):
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": event
        })

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

    # OPERATIONS
    def get_operation_description(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation description without executing."""
        method_name = f"operation_{operation_id}"
        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            func = getattr(self, method_name)

            # Basic operation description - can be extended with parameter definitions
            description = {
                "id": operation_id,
                "name": operation_id.replace("_", " ").title(),
                "description": func.__doc__ or f"Execute {operation_id} operation",
                "parameters": [],  # Can be extended to parse docstrings or use annotations
                "proximity_requirements": [],  # Could specify if physical access is needed
                "supported_modes": ["normal"]  # Could specify different operational modes
            }
            return description
        return None

    def execute_operation(self, operation_id: str, parameters: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute an operation and return execution info.
        For sync operations, returns completed result immediately.
        For async operations, would return execution ID for polling.
        """
        execution_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Check if operation exists
        method_name = f"operation_{operation_id}"
        if not (hasattr(self, method_name) and callable(getattr(self, method_name))):
            return {
                "id": execution_id,
                "status": "failed",
                "error": f"Unknown operation '{operation_id}'",
                "created_at": timestamp,
                "completed_at": timestamp
            }

        # Create execution record
        execution = {
            "id": execution_id,
            "operation_id": operation_id,
            "parameters": parameters or {},
            "status": "running",
            "created_at": timestamp,
            "completed_at": None,
            "result": None,
            "error": None
        }

        self.executions[execution_id] = execution

        try:
            # Execute the operation (currently all sync)
            func = getattr(self, method_name)
            result = func()

            # Update execution with result
            execution["status"] = "completed"
            execution["completed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            execution["result"] = {"message": result if isinstance(result, str) else str(result)}

        except Exception as e:
            execution["status"] = "failed"
            execution["completed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            execution["error"] = str(e)

        return execution

    def get_execution_status(self, operation_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific execution."""
        execution = self.executions.get(execution_id)
        if execution and execution.get("operation_id") == operation_id:
            return execution
        return None

    def run_operation(self, operation_id: str) -> dict:
        """Legacy method for backward compatibility."""
        method_name = f"operation_{operation_id}"
        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            func = getattr(self, method_name)
            result = func()
            return {"status": result if isinstance(result, str) else str(result)}
        return {"status": f"Unknown operation '{operation_id}'"}

    def list_operations(self) -> list[dict]:
        """Return a list of all available operations by scanning methods."""
        ops = []
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("operation_"):
                ops.append({
                    "id": name.replace("operation_", ""),
                    "description": func.__doc__ or ""
                })
        return ops

    # Light control operations - using modular components
    def operation_toggle_beam(self):
        """Toggle low beam."""
        response = self.operation_manager.execute_light_operation("toggle_beam_lights")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "Beam toggled")
            return result_msg
        return "Beam operation failed"

    def operation_toggle_fog(self):
        """Toggle fog lights."""
        response = self.operation_manager.execute_light_operation("toggle_fog_lights")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "Fog toggled")
            return result_msg
        return "Fog operation failed"

    def operation_toggle_front(self):
        """Toggle front lights."""
        response = self.operation_manager.execute_light_operation("toggle_front_lights")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "Front toggled")
            return result_msg
        return "Front operation failed"

    def operation_toggle_rear(self):
        """Toggle rear lights."""
        response = self.operation_manager.execute_light_operation("toggle_rear_lights")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "Rear toggled")
            return result_msg
        return "Rear operation failed"

    def operation_toggle_hazard(self):
        """Toggle hazard lights."""
        response = self.operation_manager.execute_light_operation("toggle_hazard_lights")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "Hazard toggled")
            return result_msg
        return "Hazard operation failed"

    def operation_set_all_on(self):
        """Set all lights on."""
        response = self.operation_manager.execute_light_operation("set_all_lights_on")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "All lights set to ON")
            return result_msg
        return "Set all on operation failed"

    def operation_set_all_off(self):
        """Set all lights off."""
        response = self.operation_manager.execute_light_operation("set_all_lights_off")
        if response.get("status") == "success":
            result_msg = response.get("data", {}).get("message", "All lights set to OFF")
            return result_msg
        return "Set all off operation failed"

    # DATA CATEGORIES
    def get_data_categories(self) -> List[str]:
        return self.supported_data_categories

    # METADATA
    def get_metadata(self, base_uri: str) -> Dict[str, Any]:
        base_uri = base_uri.rstrip("/")
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "vendor": self.vendor,
            "description": self.description,
            "configurations": f"{base_uri}/configuration",
            "bulk-data": f"{base_uri}/bulk-data",
            "data": f"{base_uri}/data",
            "faults": f"{base_uri}/faults",
            "operations": f"{base_uri}/operations",
            "logs": f"{base_uri}/logs",
            "data-categories": f"{base_uri}/data-categories"
        }


# Create one shared instance (pre-filled with example data)
lightctrl = LightControl(
    app_id=settings.APP_ID,
    name=settings.APP_NAME,
    version=settings.APP_VERSION,
    vendor=settings.APP_VENDOR,
    description=settings.APP_DESCRIPTION
)

# CONFIG
lightctrl.set_config("example_setting", "default")
lightctrl.set_config("max_items", 10)
lightctrl.set_config("feature_enabled", True)
lightctrl.set_config("special_feature_enabled", False)


# FAULTS
# lightctrl.add_fault({
#     "code": "modelMissing",
#     "scope": "Default",
#     "fault_name": "No Object Recognition Model available",
#     "fault_translation_id": "ALK_NoObjModel_tid",
#     "severity": 1,
#     "status": {"aggregatedStatus": "active"}
# })

# lightctrl.add_fault({
#     "code": "0012E3",
#     "scope": "Default",
#     "display_code": "P102",
#     "fault_name": "No signal from sensor",
#     "fault_translation_id": "CAMERA_0012E3_tid",
#     "severity": 1,
#     "status": {
#         "testFailed": "1",
#         "testFailedThisOperationCycle": "1",
#         "pendingDTC": "1",
#         "confirmedDTC": "1",
#         "testNotCompletedSinceLastClear": "0",
#         "testFailedSinceLastClear": "1",
#         "testNotCompletedThisOperationCycle": "0",
#         "warningIndicatorRequested": "0",
#         "aggregatedStatus": "active"
#     },
#     "environment_data": {
#         "battery_voltage": 12.8,
#         "occurence_counter": 12,
#         "first_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
#         "last_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
#     }
# })
