"""
Refactored Light Control model using modular logic components.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from logic.kuksa_client import KuksaClientManager
from logic.subscription_service import KuksaSubscriptionService
from logic.light_operations import LightOperations
from logic.sovd_data_manager import SovdDataManager
from logic.operation_manager import OperationManager
from logic.light_config import LightDataConfig

from settings import settings

logger = logging.getLogger(__name__)


class LightControl:
    """SOVD Light Control app for managing vehicle light signals."""

    def __init__(
        self,
        app_id: str,
        name: str,
        version: str,
        vendor: str,
        description: str,
        kuksa_ip: str,
        kuksa_port: int
    ):
        # Initialize core components
        self.kuksa_client = KuksaClientManager(kuksa_ip, kuksa_port)
        self.data_manager = SovdDataManager(app_id, name, version, vendor, description)
        self.light_operations = LightOperations(self.kuksa_client)
        self.operation_manager = OperationManager(self.light_operations)
        self.subscription_service = KuksaSubscriptionService(self.kuksa_client)

        # Set up cross-component communication
        self.operation_manager.set_logger(self.data_manager.add_log)
        self.subscription_service.add_update_callback(self._handle_subscription_update)

        self.data_manager.add_log("light-control started")

    def _handle_subscription_update(self, vss_path: str, new_value: Any):
        """Handle updates from KUKSA subscription service."""
        self.data_manager.update_light_state_from_subscription(vss_path, new_value)

    # KUKSA Integration Methods
    def _get_kuksa_client(self):
        """Get KUKSA client for backward compatibility."""
        return self.kuksa_client.get_client()

    async def check_kuksa_connection(self):
        """Verify connection to the KUKSA databroker."""
        success = await self.kuksa_client.check_connection()
        if success:
            self.data_manager.add_log("KUKSA connection successful.")
        else:
            self.data_manager.add_log("KUKSA connection failed.")
        return success

    async def subscribe_to_lights(self):
        """Subscribe to available light datapoints for real-time updates."""
        vss_paths = LightDataConfig.get_available_lights()
        await self.subscription_service.subscribe_to_paths(vss_paths)

    # SOVD Data Interface (backward compatibility)
    @property
    def config(self):
        return self.data_manager.config

    @property
    def data(self):
        return self.data_manager.data

    @property
    def faults(self):
        return self.data_manager.faults

    @property
    def logs(self):
        return self.data_manager.logs

    @property
    def operations(self):
        return self.data_manager.operations

    @property
    def executions(self):
        return self.operation_manager.executions

    @property
    def supported_data_categories(self):
        return self.data_manager.supported_data_categories

    @property
    def light_data(self):
        return self.data_manager.light_data

    # Configuration Methods
    def get_configurations(self) -> Dict[str, Any]:
        return self.data_manager.get_configurations()

    def set_config(self, key: str, value: Any):
        self.data_manager.set_config(key, value)

    # Data Methods
    def add_data_item(self, item: Dict[str, Any]):
        self.data_manager.add_data_item(item)

    def list_data_items(self) -> List[Dict[str, Any]]:
        return self.data_manager.list_data_items()

    def get_data_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self.data_manager.get_data_item(item_id)

    async def update_data_item(self, item_id: str, new_data: dict) -> dict:
        """Update a data item and sync with KUKSA."""
        result = await self.data_manager.update_data_item(item_id, new_data)

        # If update was successful, sync with KUKSA
        if result.get("status") == "updated" and "state" in new_data.get("data", {}):
            vss_path = LightDataConfig.get_vss_path_by_id(item_id)
            if vss_path:
                new_state = new_data["data"]["state"]
                try:
                    await self.light_operations.set_light_state(vss_path, new_state)
                except Exception as e:
                    logger.error(f"Failed to update KUKSA: {e}")

        return result

    # Log Methods
    def add_log(self, event: str):
        self.data_manager.add_log(event)

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.data_manager.get_logs()

    # Operation Methods
    def get_operation_description(self, operation_id: str) -> Optional[Dict[str, Any]]:
        return self.operation_manager.get_operation_description(operation_id)

    async def execute_operation(self, operation_id: str, parameters: Optional[Dict[str, Any]] = None) -> dict:
        return await self.operation_manager.execute_operation(operation_id, parameters)

    def get_all_operations_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions for all available operations."""
        descriptions = []
        operation_ids = self.operation_manager.get_available_operations()
        for op_id in operation_ids:
            description = self.operation_manager.get_operation_description(op_id)
            if description:
                descriptions.append(description)
        return descriptions

    # Light Operations (for backward compatibility)
    async def operation_toggle_beam(self):
        """Toggle low and high beam."""
        return await self.light_operations.toggle_beam_lights()

    async def operation_toggle_fog(self):
        """Toggle fog lights."""
        return await self.light_operations.toggle_fog_lights()

    async def operation_toggle_front(self):
        """Toggle front lights (low beam)."""
        return await self.light_operations.toggle_front_lights()

    async def operation_toggle_rear(self):
        """Toggle rear lights (brake light)."""
        return await self.light_operations.toggle_rear_lights()

    async def operation_toggle_hazard(self):
        """Toggle hazard lights."""
        return await self.light_operations.toggle_hazard_lights()

    async def operation_set_all_on(self):
        """Set all lights to ON."""
        return await self.light_operations.set_all_lights_on()

    async def operation_set_all_off(self):
        """Set all lights to OFF."""
        return await self.light_operations.set_all_lights_off()

    # Data Categories
    def get_data_categories(self) -> List[str]:
        return self.data_manager.get_data_categories()

    # Metadata
    def get_metadata(self, base_uri: str) -> Dict[str, Any]:
        return self.data_manager.get_metadata(base_uri)

    # FAULTS
    def add_fault(self, fault: Dict[str, Any]):
        self.faults.append(fault)

    def get_faults(self) -> List[Dict[str, Any]]:
        return self.faults

    def get_fault(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific fault by code"""
        return next((fault for fault in self.faults if fault.get("code") == code), None)

    def delete_fault(self, code: str) -> Dict[str, Any]:
        """Delete a specific fault by code"""
        fault = self.get_fault(code)
        if fault:
            self.faults.remove(fault)
            return {"status": "deleted", "fault": fault}
        return {"status": "not found"}

    def clear_faults(self):
        self.faults.clear()


# Create shared instance with settings
lightctrl = LightControl(
    app_id=settings.APP_ID,
    name=settings.APP_NAME,
    version=settings.APP_VERSION,
    vendor=settings.APP_VENDOR,
    description=settings.APP_DESCRIPTION,
    kuksa_ip=settings.KUKSA_IP,
    kuksa_port=settings.KUKSA_PORT
)

# Initialize default configuration
lightctrl.set_config("example_setting", "default")
lightctrl.set_config("max_items", 10)
lightctrl.set_config("feature_enabled", True)
lightctrl.set_config("special_feature_enabled", False)

# Add example fault
lightctrl.add_fault({
    "code": "B1234",
    "scope": "Default",
    "fault_name": "Brake Light Circuit Malfunction",
    "fault_translation_id": "BRAKE_LIGHT_MALFUNCTION_tid",
    "severity": 2,
    "status": {"aggregatedStatus": "active"},
    "environment_data": {
        "battery_voltage": 12.5,
        "occurence_counter": 3,
        "first_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_occurence": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
})
