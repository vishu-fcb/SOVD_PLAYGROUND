import inspect
import random
import asyncio
import uuid

from typing import List, Dict, Any, Optional
from settings import settings
from datetime import datetime, timezone

class SovdApp:
    """SOVD app container for configuration, data, faults, operations, and logs."""

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

        # AC & Room State
        self.target_temperature = 22.0
        self.ambient_temperature = 28.0

        # Register AC as data item
        self.data.append({
            "id": "AC",
            "name": "Air Conditioning",
            "category": "currentData",
            "groups": ["climate"],
            "data": {
                "Mode": "eco",
                "FanSpeed": 2,
                "unit": "level"
            }
        })

        # Register RoomTemp as data item
        self.data.append({
            "id": "RoomTemp",
            "name": "Room Temperature",
            "category": "currentData",
            "groups": ["climate"],
            "data": {
                "Temperature": 26.0,
                "unit": "°C"
            }
        })

    async def start_worker(self):
        self.add_log("Worker Started!")
        while True:
            await asyncio.sleep(2)

            ac_item = self.get_data_item("AC")
            room_item = self.get_data_item("RoomTemp")

            mode = ac_item["data"]["Mode"]
            temp = room_item["data"]["Temperature"]

            drift = random.uniform(-0.05, 0.15)

            if mode == "highspeed":
                cooling = 0.5
                temp = max(self.target_temperature, temp - cooling + drift)

            elif mode == "eco":
                cooling = 0.2
                temp = max(self.target_temperature, temp - cooling + drift)

            elif mode == "off":
                # drift back to ambient
                if temp < self.ambient_temperature:
                    temp += 0.2 + drift
                if temp > self.ambient_temperature:
                    temp = self.ambient_temperature

            room_item["data"]["Temperature"] = round(temp, 1)


    # CONFIG
    def get_configurations(self) -> Dict[str, Any]:
        return self.config

    def set_config(self, key: str, value: Any):
        self.config[key] = value

    # DATA
    def add_data_item(self, item: Dict[str, Any]):
        self.data.append(item)

    def list_data_items(self) -> List[Dict[str, Any]]:
        return self.data

    def get_data_item(self, item_id: str) -> Optional[Dict[str, Any]]:
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

        if updated_fields:
            return {"status": "updated", "updated_fields": updated_fields, "item": item}
        else:
            return {"status": "nothing to update"}

    # FAULTS
    def add_fault(self, fault: Dict[str, Any]):
        self.faults.append(fault)

    def get_faults(self) -> List[Dict[str, Any]]:
        return self.faults

    def get_fault(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific fault by code"""
        return next((fault for fault in self.faults if fault.get("code") == code), None)

    def delete_fault(self, code: str) -> Dict[str, Any]:
        """Delete a specific fault by code and return the deleted fault or status."""
        for i, fault in enumerate(self.faults):
            if fault.get("code") == code:
                deleted_fault = self.faults.pop(i)
                return deleted_fault
        return {"status": "not found"}

    def clear_faults(self):
        self.faults.clear()

    # LOGS
    def add_log(self, event: str):
        """Add a log entry with server-generated timestamp"""
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

    def execute_operation(self, operation_id: str, parameters: Optional[Dict[str, Any]] = None) -> dict:
        """Execute operation and return execution info."""
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
            # Execute operation (currently all sync)
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
        """Get execution status."""
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
        """Return list of available operations."""
        ops = []
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("operation_"):
                ops.append({
                    "id": name.replace("operation_", ""),
                    "description": func.__doc__ or ""
                })
        return ops

    def operation_set_highspeed(self):
        """Switch to highspeed mode."""
        self.ac_mode = "highspeed"
        self.ac_fan_speed = 5
        self._update_ac_data()
        self.add_log("Set AC to high")
        return f"AC set to {self.ac_mode} (fan speed {self.ac_fan_speed})"

    def operation_set_eco(self):
        """Switch to eco mode."""
        self.ac_mode = "eco"
        self.ac_fan_speed = 2
        self._update_ac_data()
        self.add_log("Set AC to eco")
        return f"AC set to {self.ac_mode} (fan speed {self.ac_fan_speed})"

    def operation_set_off(self):
        """Turn AC off."""
        self.ac_mode = "off"
        self.ac_fan_speed = 0
        self._update_ac_data()
        self.add_log("Set AC to off")
        return f"AC turned off, drifting back to {self.ambient_temperature}°C"


    # Internal helpers
    def _update_ac_data(self):
        """Keep AC data item in sync with current state."""
        for entry in self.data:
            if entry["id"] == "AC":
                entry["data"]["Mode"] = self.ac_mode
                entry["data"]["FanSpeed"] = self.ac_fan_speed

    # DATA CATEGORIES
    def set_data_categories(self, categories: List[str]):
        self.supported_data_categories = categories

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
diagnostic_app = SovdApp(
    app_id=settings.APP_ID,
    name=settings.APP_NAME,
    version=settings.APP_VERSION,
    vendor=settings.APP_VENDOR,
    description=settings.APP_DESCRIPTION
)

# CONFIG
diagnostic_app.set_config("example_setting", "default")
diagnostic_app.set_config("max_items", 10)
diagnostic_app.set_config("feature_enabled", True)
diagnostic_app.set_config("special_feature_enabled", False)

# DATA
diagnostic_app.add_data_item({
    "id": "DriverWindow",
    "name": "Position of driver window",
    "category": "currentData",
    "groups": ["front"],
    "data": {"Position": 100, "unit": "percentage"}
})

diagnostic_app.add_data_item({
    "id": "PassengerWindow",
    "name": "Position of passenger window",
    "category": "currentData",
    "groups": ["front"],
    "data": {"Position": 100, "unit": "percentage"}
})

diagnostic_app.add_data_item({
    "id": "RearWindows",
    "name": "Position of rear windows",
    "category": "currentData",
    "groups": ["rear"],
    "data": {"PositionLeft": 100, "PositionRight": 0}
})

diagnostic_app.add_data_item({
    "id": "AppInfo",
    "name": "Window Control Version Numbers",
    "category": "identData",
    "data": {"Version": "1.0.0"}
})

diagnostic_app.add_data_item({
    "id": "IO:TemperatureSensor",
    "name": "Temperature in Exemplary Location",
    "category": "currentData",
    "groups": ["front"],
    "data": {"Temperature": "22", "unit": "°C"}
})

# FAULTS
diagnostic_app.add_fault({
    "code": "modelMissing",
    "scope": "Default",
    "fault_name": "No Object Recognition Model available",
    "fault_translation_id": "ALK_NoObjModel_tid",
    "severity": 1,
    "status": {"aggregatedStatus": "active"}
})

diagnostic_app.add_fault({
    "code": "0012E3",
    "scope": "Default",
    "display_code": "P102",
    "fault_name": "No signal from sensor",
    "fault_translation_id": "CAMERA_0012E3_tid",
    "severity": 1,
    "status": {
        "testFailed": "1",
        "testFailedThisOperationCycle": "1",
        "pendingDTC": "1",
        "confirmedDTC": "1",
        "testNotCompletedSinceLastClear": "0",
        "testFailedSinceLastClear": "1",
        "testNotCompletedThisOperationCycle": "0",
        "warningIndicatorRequested": "0",
        "aggregatedStatus": "active"
    },
    "environment_data": {
        "battery_voltage": 12.8,
        "occurence_counter": 12,
        "first_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
})

# LOGS
diagnostic_app.add_log("app_started")

# DATA CATEGORIES
diagnostic_app.set_data_categories([
    "currentData",
    "identData",
    "storedData",
    "sysInfo"
])
