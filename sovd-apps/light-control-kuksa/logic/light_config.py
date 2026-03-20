"""
Light data definitions and configuration for the light control system.
"""

from sovd.datatypes import DataItem, DataCategory


class LightDataConfig:
    """Configuration for all supported light types and their VSS paths."""

    # VSS path to DataItem mapping for KUKSA integration
    LIGHT_DATA_KUKSA = {
        "Vehicle.Body.Lights.Beam.Low.IsOn": DataItem(
            id="BeamLow",
            name="Beam Low",
            category=DataCategory.CURRENT_DATA,
            groups=["beam", "front"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.Beam.High.IsOn": DataItem(
            id="BeamHigh",
            name="Beam High",
            category=DataCategory.CURRENT_DATA,
            groups=["beam", "front"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.Fog.Front.IsOn": DataItem(
            id="FogFront",
            name="Fog Front",
            category=DataCategory.CURRENT_DATA,
            groups=["fog", "front"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.Fog.Rear.IsOn": DataItem(
            id="FogRear",
            name="Fog Rear",
            category=DataCategory.CURRENT_DATA,
            groups=["fog", "rear"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling": DataItem(
            id="IndicatorLeft",
            name="IndicatorLeft",
            category=DataCategory.CURRENT_DATA,
            groups=["indicator", "left"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling": DataItem(
            id="IndicatorRight",
            name="IndicatorRight",
            category=DataCategory.CURRENT_DATA,
            groups=["indicator", "right"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.Backup.IsOn": DataItem(
            id="Backup",
            name="Backup",
            category=DataCategory.CURRENT_DATA,
            groups=["rear"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.Brake.IsActive": DataItem(
            id="Brake",
            name="Brake",
            category=DataCategory.CURRENT_DATA,
            groups=["rear"],
            data={"state": None}
        ),
        "Vehicle.Cabin.Light.IsDomeOn": DataItem(
            id="Dome",
            name="Dome",
            category=DataCategory.CURRENT_DATA,
            groups=["interieur"],
            data={"state": None}
        ),
        "Vehicle.Body.Lights.IsHazardOn": DataItem(
            id="Hazard",
            name="Hazard",
            category=DataCategory.CURRENT_DATA,
            groups=["exterior"],
            data={"state": None}
        ),
    }

    # Light groups for batch operations
    BEAM_LIGHTS = [
        "Vehicle.Body.Lights.Beam.Low.IsOn",
        "Vehicle.Body.Lights.Beam.High.IsOn"
    ]

    FOG_LIGHTS = [
        "Vehicle.Body.Lights.Fog.Front.IsOn",
        "Vehicle.Body.Lights.Fog.Rear.IsOn"
    ]

    INDICATOR_LIGHTS = [
        "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling",
        "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling"
    ]

    # Available lights for batch operations (excluding problematic paths)
    AVAILABLE_LIGHTS = [
        "Vehicle.Body.Lights.Beam.Low.IsOn",
        "Vehicle.Body.Lights.Beam.High.IsOn",
        "Vehicle.Body.Lights.Fog.Front.IsOn",
        "Vehicle.Body.Lights.Fog.Rear.IsOn",
        "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling",
        "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling",
        "Vehicle.Body.Lights.Backup.IsOn",
        "Vehicle.Body.Lights.Brake.IsActive",
        "Vehicle.Cabin.Light.IsDomeOn"
        # Note: Vehicle.Body.Lights.IsHazardOn excluded from batch operations
    ]

    # All lights including those that might not be available (for configuration/display purposes)
    ALL_LIGHTS = list(LIGHT_DATA_KUKSA.keys())

    @classmethod
    def get_light_data(cls):
        """Get a copy of the light data configuration."""
        return cls.LIGHT_DATA_KUKSA.copy()

    @classmethod
    def get_available_lights(cls):
        """Get list of VSS paths that are actually available in KUKSA (safe for batch operations)."""
        return cls.AVAILABLE_LIGHTS.copy()

    @classmethod
    def get_vss_path_by_id(cls, item_id: str) -> str:
        """Find VSS path by light item ID."""
        for vss_path, data_item in cls.LIGHT_DATA_KUKSA.items():
            if data_item.id == item_id:
                return vss_path
        return None

    @classmethod
    def get_data_item_by_id(cls, item_id: str) -> DataItem:
        """Find DataItem by light item ID."""
        for data_item in cls.LIGHT_DATA_KUKSA.values():
            if data_item.id == item_id:
                return data_item
        return None
