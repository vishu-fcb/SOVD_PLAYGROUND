"""
SOVD data management and API integration layer.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .light_config import LightDataConfig


class SovdDataManager:
    """Manages SOVD data items, logs, configurations, and operations."""

    def __init__(self, app_id: str, name: str, version: str, vendor: str, description: str):
        # Metadata
        self.id = app_id
        self.name = name
        self.version = version
        self.vendor = vendor
        self.description = description

        # Core SOVD resources
        self.config: Dict[str, Any] = {}
        self.data: List[Dict[str, Any]] = []
        self.faults: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self.operations: List[Dict[str, Any]] = []
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.supported_data_categories: List[str] = []

        # Light data mapping (VSS path -> DataItem)
        self.light_data = LightDataConfig.get_light_data()

        self._initialize_data()

    def _initialize_data(self):
        """Initialize SOVD data items from light configuration."""
        self.data.clear()

        # Add light data items
        for vss_path, data_item in self.light_data.items():
            self.add_data_item({
                "id": data_item.id,
                "name": data_item.name,
                "category": data_item.category,
                "groups": data_item.groups,
                "data": data_item.data.copy(),
            })

        # Add app info
        self.add_data_item({
            "id": "AppInfo",
            "name": "Light Control Version",
            "category": "identData",
            "data": {"Version": self.version}
        })

    # CONFIG MANAGEMENT
    def get_configurations(self) -> Dict[str, Any]:
        return self.config

    def set_config(self, key: str, value: Any):
        self.config[key] = value
        self.add_log(f"{key} was set to {value}")

    # DATA MANAGEMENT
    def add_data_item(self, item: Dict[str, Any]):
        self.data.append(item)

    def list_data_items(self) -> List[Dict[str, Any]]:
        return self.data

    def get_data_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single data item by ID."""
        return next((d for d in self.data if d.get("id") == item_id), None)

    async def update_data_item(self, item_id: str, new_data: dict) -> dict:
        """Update a data item and sync with KUKSA if needed."""
        item = self.get_data_item(item_id)
        if not item:
            return {"status": "not found"}

        if "data" in new_data and isinstance(new_data["data"], dict) and "state" in new_data["data"]:
            new_state = new_data["data"]["state"]
            item["data"]["state"] = new_state

            # Update internal light data
            vss_path = LightDataConfig.get_vss_path_by_id(item_id)
            if vss_path and vss_path in self.light_data:
                self.light_data[vss_path].data["state"] = new_state

            self.add_log(f"Updated {item_id} to {new_state}")
            return {"status": "updated", "updated_fields": ["state"], "item": item}

        return {"status": "nothing to update", "item": item}

    def update_light_state_from_subscription(self, vss_path: str, new_value: Any):
        """Update light state from KUKSA subscription."""
        if vss_path not in self.light_data:
            return

        # Update internal data
        self.light_data[vss_path].data['state'] = new_value

        # Update exposed API data
        item_id = self.light_data[vss_path].id
        for api_item in self.data:
            if api_item.get("id") == item_id:
                api_item['data']['state'] = new_value
                break

        self.add_log(f"Subscription update: {item_id} is now {new_value}")

    # LOG MANAGEMENT
    def add_log(self, event: str):
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": event
        })

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

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

    def get_data_categories(self) -> List[str]:
        return self.supported_data_categories
