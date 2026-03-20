from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# DATA
class DataPayload(BaseModel):
    data: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "Mode": "eco",
                        "FanSpeed": 2,
                        "unit": "level"
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
                    "id": "AC",
                    "name": "Air Conditioning",
                    "category": "currentData",
                    "groups": ["climate"],
                    "data": {"Mode": "eco", "FanSpeed": 2, "unit": "level"}
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
                            "id": "AC",
                            "name": "Air Conditioning",
                            "category": "currentData",
                            "groups": ["climate"],
                            "data": {"Mode": "eco", "FanSpeed": 2, "unit": "level"}
                        },
                        {
                            "id": "RoomTemp",
                            "name": "Room Temperature",
                            "category": "currentData",
                            "groups": ["climate"],
                            "data": {"Temperature": 22, "unit": "°C"}
                        },
                        {
                            "id": "AppInfo",
                            "name": "Window Control Version Numbers",
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
                {"event": "AC system started"},
                {"event": "Temperature adjusted to 22°C"}
            ]
        }
    }

class LogItem(BaseModel):
    timestamp: str
    event: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2025-10-21T10:30:00Z",
                    "event": "AC system started"
                }
            ]
        }
    }

class LogList(BaseModel):
    logs: List[LogItem]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "logs": [
                        {
                            "timestamp": "2025-10-21T10:30:00Z",
                            "event": "AC system started"
                        },
                        {
                            "timestamp": "2025-10-21T14:15:30Z",
                            "event": "Temperature adjusted to 22°C"
                        }
                    ]
                }
            ]
        }
    }


# CONFIG
class ConfigResponse(BaseModel):
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

class ConfigUpdate(BaseModel):
    value: Any
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "value": 22
                }
            ]
        }
    }


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
                    "code": "0012E3",
                    "scope": "Default",
                    "fault_name": "No signal from sensor",
                    "severity": 1,
                    "status": {
                        "aggregatedStatus": "active",
                        "testFailed": "1",
                        "confirmedDTC": "1"
                    },
                    "display_code": "P102",
                    "fault_translation_id": "CAMERA_0012E3_tid"
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
                            "code": "modelMissing",
                            "scope": "Default",
                            "fault_name": "No Object Recognition Model available",
                            "severity": 1,
                            "status": {
                                "aggregatedStatus": "active",
                                "testFailed": None,
                                "confirmedDTC": None
                            },
                            "display_code": None,
                            "fault_translation_id": "ALK_NoObjModel_tid"
                        },
                        {
                            "code": "0012E3",
                            "scope": "Default",
                            "fault_name": "No signal from sensor",
                            "severity": 1,
                            "status": {
                                "aggregatedStatus": "active",
                                "testFailed": "1",
                                "confirmedDTC": "1"
                            },
                            "display_code": "P102",
                            "fault_translation_id": "CAMERA_0012E3_tid"
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
                    "id": "set_eco",
                    "name": "Set Eco",
                    "description": "Switch to eco mode.",
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
                            "id": "set_eco",
                            "description": "Switch to eco mode."
                        },
                        {
                            "id": "set_highspeed",
                            "description": "Switch to highspeed mode."
                        },
                        {
                            "id": "set_off",
                            "description": "Turn AC off."
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
                    "id": "5b990fc1-169f-4079-8384-e45f7dac4004",
                    "status": "completed",
                    "result": {"message": "AC set to eco (fan speed 2)"},
                    "error": None,
                    "created_at": "2025-10-22T17:23:16Z",
                    "completed_at": "2025-10-22T17:23:16Z"
                }
            ]
        }
    }

class OperationResult(BaseModel):
    status: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success"
                }
            ]
        }
    }

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
                    "key": "max_items",
                    "value": 22
                }
            ]
        }
    }

class StatusResponse(BaseModel):
    """Generic status response"""
    status: str
    message: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "Fault cleared successfully"
                }
            ]
        }
    }

class Problem(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs"""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
