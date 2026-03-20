"""AC control configuration endpoints"""

from fastapi import APIRouter, HTTPException, Path
from .model import diagnostic_app
from .datatypes import ConfigurationResponse, ConfigurationUpdateResponse, ConfigUpdate

router = APIRouter()

@router.get("/configuration",
    response_model=ConfigurationResponse,
    summary="Get configuration",
    description="Retrieves all AC control configuration parameters including temperature settings, fan speed preferences, climate zones, and operational modes",
    tags=["Configuration"]
)
def get_configuration():
    """Get all configuration values"""
    return {"configuration": diagnostic_app.get_configurations()}

@router.put("/configuration/{key}",
    response_model=ConfigurationUpdateResponse,
    summary="Update configuration",
    description="Updates a single AC configuration parameter by key. Use this to adjust temperature, fan speed, climate zones, or enable/disable auto climate control",
    tags=["Configuration"]
)
def update_configuration(payload: ConfigUpdate, key: str = Path(..., description="The configuration key to update")):
    """Update a configuration parameter"""
    if not hasattr(payload, 'value'):
        raise HTTPException(status_code=400, detail="Payload must include 'value'")

    diagnostic_app.set_config(key, payload.value)
    return {
        "status": "updated",
        "key": key,
        "value": diagnostic_app.get_configurations()[key]
    }
