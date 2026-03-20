from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# GATEWAY RESPONSE SCHEMAS

class ServerInfo(BaseModel):
    """Server information model."""
    name: str
    url: str
    status: str
    metadata: Optional[Dict[str, Any]] = {}

class DiscoveredServer(BaseModel):
    """Discovered server information model."""
    name: str
    url: str
    status: str

class DiscoveryResponse(BaseModel):
    """Response model for server discovery."""
    message: str
    discovered_servers: List[DiscoveredServer]
    docs_url: str

class RegistrationResponse(BaseModel):
    """Response model for server registration."""
    message: str
    name: str
    url: str
    type: str

class ServersListResponse(BaseModel):
    """Response model for listing servers."""
    servers: Dict[str, Any]  # Dict mapping server_name -> server_info
    count: int

class EndpointMappingResponse(BaseModel):
    """Response model for endpoint mapping."""
    endpoint_mapping: Dict[str, Dict[str, str]]  # Dict mapping method -> path -> server_name
    description: str

class RefreshResponse(BaseModel):
    """Response model for documentation refresh."""
    message: str

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    type: str

class Problem(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
