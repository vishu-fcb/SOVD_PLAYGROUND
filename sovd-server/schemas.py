from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# SERVER RESPONSE SCHEMAS
class RegistrationDebugResponse(BaseModel):
    # Debug registration response
    status: str

class RegistrationResponse(BaseModel):
    # Service registration response
    message: str
    name: str
    url: str
    type: str

class ServicesListResponse(BaseModel):
    # Response for listing services
    services: List[Dict[str, Any]]
    count: int

class RefreshResponse(BaseModel):
    # Response for documentation refresh
    message: str

class HealthResponse(BaseModel):
    # Health check response
    status: str
    version: str

class Problem(BaseModel):
    # RFC 7807 Problem Details for HTTP APIs
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
