from typing import Dict, Any, Optional
from .light_operations import LightOperations
from .sovd_data_manager import SovdDataManager
from .light_config import LightDataConfig


class OperationManager:

    def __init__(self):
        self.light_ops = LightOperations()
        self.sovd_manager = SovdDataManager()

    def execute_light_operation(self, operation: str, light_key: Optional[str] = None) -> Dict[str, Any]:
        try:
            result = None

            # Individual light operations
            if operation == "toggle" and light_key:
                if self.sovd_manager.validate_light_operation(light_key):
                    new_state = self.light_ops.toggle_light(light_key)
                    result = f"{light_key} is set to {'ON' if new_state else 'OFF'}"
                else:
                    return self.sovd_manager.format_error_response(
                        operation, f"Invalid light key: {light_key}"
                    )

            # Group operations
            elif operation == "toggle_beam_lights":
                result = self.light_ops.toggle_beam_lights()
            elif operation == "toggle_fog_lights":
                result = self.light_ops.toggle_fog_lights()
            elif operation == "toggle_front_lights":
                result = self.light_ops.toggle_front_lights()
            elif operation == "toggle_rear_lights":
                result = self.light_ops.toggle_rear_lights()
            elif operation == "toggle_hazard_lights":
                result = self.light_ops.toggle_hazard_lights()
            elif operation == "set_all_lights_on":
                result = self.light_ops.set_all_lights_on()
            elif operation == "set_all_lights_off":
                result = self.light_ops.set_all_lights_off()

            # Status operations
            elif operation == "get_all_lights":
                current_states = self.get_all_light_states()
                formatted_data = self.sovd_manager.format_light_data(current_states)
                return self.sovd_manager.create_sovd_response("get_all_lights", formatted_data)

            elif operation == "get_light_summary":
                current_states = self.get_all_light_states()
                summary = self.sovd_manager.get_light_summary(current_states)
                return self.sovd_manager.create_sovd_response("get_light_summary", summary)

            elif operation == "get_available_operations":
                operations = self.sovd_manager.get_available_operations()
                return self.sovd_manager.create_sovd_response("get_available_operations", operations)

            else:
                return self.sovd_manager.format_error_response(
                    operation, f"Unknown operation: {operation}"
                )

            # For operations that modify state, return current states
            if result:
                current_states = self.get_all_light_states()
                response_data = {
                    "message": result,
                    "current_states": self.sovd_manager.format_light_data(current_states)
                }
                return self.sovd_manager.create_sovd_response(operation, response_data)

        except Exception as e:
            return self.sovd_manager.format_error_response(
                operation, f"Operation failed: {str(e)}"
            )

    def get_all_light_states(self) -> Dict[str, bool]:
        return {light_key: self.light_ops.get_light_state(light_key)
                for light_key in LightDataConfig.ALL_LIGHTS}

    def set_multiple_lights(self, light_states: Dict[str, bool]) -> Dict[str, Any]:
        try:
            # Validate all light keys first
            invalid_keys = [key for key in light_states.keys()
                          if not self.sovd_manager.validate_light_operation(key)]

            if invalid_keys:
                return self.sovd_manager.format_error_response(
                    "set_multiple_lights", f"Invalid light keys: {invalid_keys}"
                )

            # Set the lights
            success = self.light_ops.set_multiple_lights(light_states)

            if success:
                current_states = self.get_all_light_states()
                response_data = {
                    "message": f"Successfully set {len(light_states)} lights",
                    "current_states": self.sovd_manager.format_light_data(current_states)
                }
                return self.sovd_manager.create_sovd_response("set_multiple_lights", response_data)
            else:
                return self.sovd_manager.format_error_response(
                    "set_multiple_lights", "Failed to set lights"
                )

        except Exception as e:
            return self.sovd_manager.format_error_response(
                "set_multiple_lights", f"Operation failed: {str(e)}"
            )

    def get_light_info(self, light_key: str) -> Dict[str, Any]:
        try:
            if not self.sovd_manager.validate_light_operation(light_key):
                return self.sovd_manager.format_error_response(
                    "get_light_info", f"Invalid light key: {light_key}"
                )

            metadata = self.sovd_manager.get_light_metadata(light_key)
            current_state = self.light_ops.get_light_state(light_key)

            light_info = {
                **metadata,
                "current_state": current_state,
                "light_key": light_key
            }

            return self.sovd_manager.create_sovd_response("get_light_info", light_info)

        except Exception as e:
            return self.sovd_manager.format_error_response(
                "get_light_info", f"Operation failed: {str(e)}"
            )
