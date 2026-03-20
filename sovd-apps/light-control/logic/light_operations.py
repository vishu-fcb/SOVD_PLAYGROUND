from typing import Dict
from .light_config import LightDataConfig


class LightOperations:
    def __init__(self):
        self.light_states = {}
        # Initialize all lights to False
        for light_key in LightDataConfig.ALL_LIGHTS:
            self.light_states[light_key] = False

    def toggle_light(self, light_key: str) -> bool:
        if light_key in self.light_states:
            self.light_states[light_key] = not self.light_states[light_key]
            return self.light_states[light_key]
        return False

    def set_light_state(self, light_key: str, state: bool) -> bool:
        if light_key in self.light_states:
            self.light_states[light_key] = state
            return True
        return False

    def get_light_state(self, light_key: str) -> bool:
        return self.light_states.get(light_key, False)

    def set_multiple_lights(self, light_states: Dict[str, bool]) -> bool:
        for light_key, state in light_states.items():
            if light_key in self.light_states:
                self.light_states[light_key] = state
        return True

    # Predefined operations
    def toggle_beam_lights(self) -> str:
        states = []
        for light_key in LightDataConfig.BEAM_LIGHTS:
            new_state = self.toggle_light(light_key)
            states.append(new_state)
        return f"Beam is set to {'ON' if states[0] else 'OFF'}"

    def toggle_fog_lights(self) -> str:
        states = []
        for light_key in LightDataConfig.FOG_LIGHTS:
            new_state = self.toggle_light(light_key)
            states.append(new_state)
        return f"Fog is set to {'ON' if states[0] else 'OFF'}"

    def toggle_front_lights(self) -> str:
        new_state = self.toggle_light('beam_low')
        return f"Front light is set to {'ON' if new_state else 'OFF'}"

    def toggle_rear_lights(self) -> str:
        new_state = self.toggle_light('brake')
        return f"Rear light is set to {'ON' if new_state else 'OFF'}"

    def toggle_hazard_lights(self) -> str:
        states = []
        for light_key in LightDataConfig.INDICATOR_LIGHTS:
            new_state = self.toggle_light(light_key)
            states.append(new_state)
        return f"Hazard is set to {'ON' if states[0] else 'OFF'}"

    def set_all_lights_on(self) -> str:
        for light_key in LightDataConfig.ALL_LIGHTS:
            self.light_states[light_key] = True
        return "All lights are set to ON"

    def set_all_lights_off(self) -> str:
        for light_key in LightDataConfig.ALL_LIGHTS:
            self.light_states[light_key] = False
        return "All lights are set to OFF"
