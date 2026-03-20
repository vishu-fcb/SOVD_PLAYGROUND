from typing import Dict, Any
from datetime import datetime

from .light_config import LightDataConfig


class SovdDataManager:

    def __init__(self):
        self.sovd_data = {}

    def format_light_data(self, light_states: Dict[str, bool]) -> Dict[str, Any]:
        formatted_data = {}

        for light_key, state in light_states.items():
            if light_key in LightDataConfig.LIGHT_DATA_BASIC:
                light_config = LightDataConfig.LIGHT_DATA_BASIC[light_key]
                formatted_data[light_key] = {
                    "description": light_config["description"],
                    "type": light_config["type"],
                    "state": state,
                    "timestamp": self._get_current_timestamp()
                }

        return formatted_data

    def create_sovd_response(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "operation": operation,
            "timestamp": self._get_current_timestamp(),
            "status": "success",
            "data": data
        }

    def get_light_summary(self, light_states: Dict[str, bool]) -> Dict[str, Any]:
        summary = {
            "beam_lights": {},
            "fog_lights": {},
            "indicator_lights": {},
            "other_lights": {}
        }

        for light_key, state in light_states.items():
            if light_key in LightDataConfig.BEAM_LIGHTS:
                summary["beam_lights"][light_key] = state
            elif light_key in LightDataConfig.FOG_LIGHTS:
                summary["fog_lights"][light_key] = state
            elif light_key in LightDataConfig.INDICATOR_LIGHTS:
                summary["indicator_lights"][light_key] = state
            else:
                summary["other_lights"][light_key] = state

        return summary

    def validate_light_operation(self, light_key: str) -> bool:
        return light_key in LightDataConfig.ALL_LIGHTS

    def get_available_operations(self) -> Dict[str, Any]:
        return {
            "individual_lights": list(LightDataConfig.ALL_LIGHTS),
            "group_operations": [
                "toggle_beam_lights",
                "toggle_fog_lights",
                "toggle_front_lights",
                "toggle_rear_lights",
                "toggle_hazard_lights",
                "set_all_lights_on",
                "set_all_lights_off"
            ],
            "light_categories": {
                "beam": list(LightDataConfig.BEAM_LIGHTS),
                "fog": list(LightDataConfig.FOG_LIGHTS),
                "indicator": list(LightDataConfig.INDICATOR_LIGHTS)
            }
        }

    def _get_current_timestamp(self) -> str:
        return datetime.now().isoformat()

    def get_light_metadata(self, light_key: str) -> Dict[str, Any]:
        if light_key in LightDataConfig.LIGHT_DATA_BASIC:
            return LightDataConfig.LIGHT_DATA_BASIC[light_key].copy()
        return {}

    def format_error_response(self, operation: str, error_message: str) -> Dict[str, Any]:
        return {
            "operation": operation,
            "timestamp": self._get_current_timestamp(),
            "status": "error",
            "error": error_message
        }
