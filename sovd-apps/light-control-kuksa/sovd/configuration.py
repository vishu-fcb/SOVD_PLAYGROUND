"""Light control configuration endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import lightctrl
from .datatypes import ConfigurationResponse, ConfigurationUpdateResponse, ConfigUpdate

router = APIRouter()

@router.get("/configuration",
    response_model=ConfigurationResponse,
    summary="Get configuration",
    description="Retrieves all light control configuration parameters including brightness, auto mode settings, and operational thresholds (Kuksa-enabled version)",
    tags=["Configuration"]
)
def get_configuration():
    """Get all configuration values"""
    return {"configuration": lightctrl.get_configurations()}

@router.put("/configuration/{key}",
    response_model=ConfigurationUpdateResponse,
    summary="Update configuration",
    description="Updates a single light control configuration parameter by key. Use this to adjust brightness levels, enable/disable auto mode, or modify operational thresholds (Kuksa-enabled version)",
    tags=["Configuration"]
)
def update_configuration(payload: ConfigUpdate, key: str = Path(..., description="The configuration key to update")):
    """Update a configuration parameter"""
    if not hasattr(payload, 'value'):
        raise HTTPException(status_code=400, detail="Payload must include 'value'")

    lightctrl.set_config(key, payload.value)
    return {
        "status": "updated",
        "key": key,
        "value": lightctrl.get_configurations()[key]
    }
