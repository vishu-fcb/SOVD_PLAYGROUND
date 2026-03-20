"""
Light control operations and business logic.
"""

from typing import Dict

from .kuksa_client import KuksaClientManager
from .light_config import LightDataConfig


class LightOperations:
    """Handles light control operations and state management."""

    def __init__(self, client_manager: KuksaClientManager):
        self.client_manager = client_manager

    async def toggle_light(self, vss_path: str, *additional_paths: str) -> bool:
        """Toggle a light and return the new state."""
        # Get current state
        current_value = await self.client_manager.get_datapoint(vss_path)
        new_state = not bool(current_value) if current_value is not None else True

        # Set all specified paths to the new state
        paths_to_update = [vss_path] + list(additional_paths)
        datapoints = {path: new_state for path in paths_to_update}

        success = await self.client_manager.set_datapoints(datapoints)
        return new_state if success else current_value

    async def set_light_state(self, vss_path: str, state: bool) -> bool:
        """Set a specific light to the given state."""
        return await self.client_manager.set_datapoint(vss_path, state)

    async def set_multiple_lights(self, light_states: Dict[str, bool]) -> bool:
        """Set multiple lights to their specified states."""
        return await self.client_manager.set_datapoints(light_states)

    # Predefined operations for common light groups
    async def toggle_beam_lights(self) -> str:
        """Toggle low and high beam."""
        new_state = await self.toggle_light(*LightDataConfig.BEAM_LIGHTS)
        return f"Beam is set to {'ON' if new_state else 'OFF'}"

    async def toggle_fog_lights(self) -> str:
        """Toggle fog lights."""
        new_state = await self.toggle_light(*LightDataConfig.FOG_LIGHTS)
        return f"Fog is set to {'ON' if new_state else 'OFF'}"

    async def toggle_front_lights(self) -> str:
        """Toggle front lights (low beam)."""
        new_state = await self.toggle_light('Vehicle.Body.Lights.Beam.Low.IsOn')
        return f"Front light is set to {'ON' if new_state else 'OFF'}"

    async def toggle_rear_lights(self) -> str:
        """Toggle rear lights (brake light)."""
        new_state = await self.toggle_light('Vehicle.Body.Lights.Brake.IsActive')
        return f"Rear light is set to {'ON' if new_state else 'OFF'}"

    async def toggle_hazard_lights(self) -> str:
        """Toggle hazard lights."""
        # Workaround: Toggle both indicators since IsHazardOn is not on CAN
        new_state = await self.toggle_light(*LightDataConfig.INDICATOR_LIGHTS)
        return f"Hazard is set to {'ON' if new_state else 'OFF'}"

    async def set_all_lights_on(self) -> str:
        """Set all lights to ON."""
        datapoints = {light: True for light in LightDataConfig.get_available_lights()}
        success = await self.client_manager.set_datapoints(datapoints)
        return "All lights are set to ON" if success else "Failed to set all lights ON"

    async def set_all_lights_off(self) -> str:
        """Set all lights to OFF."""
        datapoints = {light: False for light in LightDataConfig.get_available_lights()}
        success = await self.client_manager.set_datapoints(datapoints)
        return "All lights are set to OFF" if success else "Failed to set all lights OFF"
