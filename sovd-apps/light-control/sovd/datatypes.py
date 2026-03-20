from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel

class DataCategory(Enum):
    CURRENT_DATA = "currentData"
    IDENT_DATA = "identData"
    STORED_DATA = "storedData"
    SYS_INFO = "sysInfo"

# DATA
class DataPayload(BaseModel):
    data: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "state": True
                    }
                }
            ]
        }
    }

class DataItem(BaseModel):
    id: str
    name: str
    category: str
    groups: Optional[List[str]] = None
    data: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "Dome",
                    "name": "Dome",
                    "category": "currentData",
                    "groups": ["interieur"],
                    "data": {"state": None}
                }
            ]
        }
    }

class DataList(BaseModel):
    items: List[DataItem]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {
                            "id": "BeamLow",
                            "name": "Beam Low",
                            "category": "currentData",
                            "groups": ["beam", "front"],
                            "data": {"state": None}
                        },
                        {
                            "id": "Dome",
                            "name": "Dome",
                            "category": "currentData",
                            "groups": ["interieur"],
                            "data": {"state": None}
                        },
                        {
                            "id": "AppInfo",
                            "name": "Light Control Version",
                            "category": "identData",
                            "groups": None,
                            "data": {"Version": "1.0.0"}
                        }
                    ]
                }
            ]
        }
    }


# LOGS
class LogEntry(BaseModel):
    event: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"event": "Light control system started"},
                {"event": "Hazard lights activated"}
            ]
        }
    }

class LogItem(BaseModel):
    timestamp: str
    event:str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2025-10-21T10:30:00Z",
                    "event": "Beam lights toggled"
                }
            ]
        }
    }

class LogList(BaseModel):
    logs: List[LogItem]


# CONFIG
class ConfigResponse(BaseModel):
    configuration: Dict[str, Any]

class ConfigUpdate(BaseModel):
    value: Any


# FAULTS
class Fault(BaseModel):
    code: str
    scope: str
    fault_name: str
    severity: int
    status: Dict[str, Optional[str]]  # Inlined to avoid nested schema issues with FastMCP
    display_code: Optional[str] = None
    fault_translation_id: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "B1234",
                    "scope": "Default",
                    "fault_name": "Brake Light Circuit Malfunction",
                    "severity": 2,
                    "status": {
                        "aggregatedStatus": "active",
                        "testFailed": None,
                        "confirmedDTC": None
                    },
                    "display_code": None,
                    "fault_translation_id": "BRAKE_LIGHT_MALFUNCTION_tid"
                }
            ]
        }
    }

class FaultList(BaseModel):
    items: List[Fault]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {
                            "code": "B1234",
                            "scope": "Default",
                            "fault_name": "Brake Light Circuit Malfunction",
                            "severity": 2,
                            "status": {
                                "aggregatedStatus": "active",
                                "testFailed": None,
                                "confirmedDTC": None
                            },
                            "display_code": None,
                            "fault_translation_id": "BRAKE_LIGHT_MALFUNCTION_tid"
                        }
                    ]
                }
            ]
        }
    }


# OPERATIONS
class OperationParameter(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None

class OperationDescription(BaseModel):
    id: str
    name: str
    description: str
    parameters: Optional[List[OperationParameter]] = []
    proximity_requirements: Optional[List[str]] = []
    supported_modes: Optional[List[str]] = []
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "toggle_hazard_lights",
                    "name": "Toggle Hazard Lights",
                    "description": "Toggle hazard lights.",
                    "parameters": [],
                    "proximity_requirements": [],
                    "supported_modes": ["normal"]
                }
            ]
        }
    }

class Operation(BaseModel):
    id: str
    description: str

class OperationList(BaseModel):
    operations: List[Operation]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operations": [
                        {
                            "id": "toggle_hazard_lights",
                            "description": "Toggle hazard lights."
                        },
                        {
                            "id": "set_all_lights_off",
                            "description": "Set all lights to OFF."
                        },
                        {
                            "id": "toggle_beam_lights",
                            "description": "Toggle low and high beam."
                        }
                    ]
                }
            ]
        }
    }

class ExecutionRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = {}
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "parameters": {}
                }
            ]
        }
    }

class ExecutionResult(BaseModel):
    id: str
    status: str  # "running", "completed", "failed"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "cf9a7c7c-2562-4c5b-b7f0-85657a164068",
                    "status": "completed",
                    "result": "Hazard is set to ON",
                    "error": None,
                    "created_at": "2025-10-22T17:49:05Z",
                    "completed_at": "2025-10-22T17:49:05Z"
                }
            ]
        }
    }

class OperationResult(BaseModel):
    status: str

# COMMON RESPONSE SCHEMAS
class ConfigurationResponse(BaseModel):
    """Response containing configuration values"""
    configuration: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "configuration": {
                        "example_setting": "default",
                        "max_items": 10,
                        "feature_enabled": True,
                        "special_feature_enabled": False
                    }
                }
            ]
        }
    }

class ConfigurationUpdateResponse(BaseModel):
    """Response after updating a configuration value"""
    status: str
    key: str
    value: Any
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "updated",
                    "key": "feature_enabled",
                    "value": True
                }
            ]
        }
    }

class StatusResponse(BaseModel):
    """Generic status response"""
    status: str
    message: Optional[str] = None

class Problem(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs"""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
