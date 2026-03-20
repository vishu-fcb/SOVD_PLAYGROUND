class LightDataConfig:
    LIGHT_DATA_BASIC = {
        "beam_low": {
            "description": "Beam Low",
            "type": "beam"
        },
        "beam_high": {
            "description": "Beam High",
            "type": "beam"
        },
        "fog_front": {
            "description": "Fog Front",
            "type": "fog"
        },
        "fog_rear": {
            "description": "Fog Rear",
            "type": "fog"
        },
        "indicator_left": {
            "description": "Indicator Left",
            "type": "indicator"
        },
        "indicator_right": {
            "description": "Indicator Right",
            "type": "indicator"
        },
        "backup": {
            "description": "Backup",
            "type": "rear"
        },
        "brake": {
            "description": "Brake",
            "type": "rear"
        },
        "dome": {
            "description": "Dome",
            "type": "interior"
        },
    }

    # Light groups
    BEAM_LIGHTS = ["beam_low", "beam_high"]
    FOG_LIGHTS = ["fog_front", "fog_rear"]
    INDICATOR_LIGHTS = ["indicator_left", "indicator_right"]
    ALL_LIGHTS = list(LIGHT_DATA_BASIC.keys())

    @classmethod
    def get_light_data(cls):
        return cls.LIGHT_DATA_BASIC.copy()

    @classmethod
    def get_data_item_by_id(cls, item_id: str):
        for key, light_config in cls.LIGHT_DATA_BASIC.items():
            if light_config["description"].replace(" ", "") == item_id:
                return light_config
        return None

    @classmethod
    def get_light_key_by_id(cls, item_id: str) -> str:
        for key, light_config in cls.LIGHT_DATA_BASIC.items():
            if light_config["description"].replace(" ", "") == item_id:
                return key
        return None
