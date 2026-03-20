import logging
from typing import Dict, Any, Optional, Literal, TypedDict

logger = logging.getLogger(__name__)

EntityType = Literal["server", "component"]

class ServerEntry(TypedDict):
    """Server registry entry type"""
    url: str
    metadata: Dict[str, Any]
    status: str

class ComponentEntry(TypedDict):
    """Component registry entry type"""
    pass  # Add specific fields as needed

# Registry data stores
SERVER_REGISTRY: Dict[str, ServerEntry] = {}
COMPONENT_REGISTRY: Dict[str, ComponentEntry] = {}

def register_entity(name: str, entity_type: EntityType, entry: Dict[str, Any]) -> None:
    """Register a SOVD server or component in the registry."""
    if entity_type == "server":
        SERVER_REGISTRY[name] = entry
        logger.info(f"Registered SOVD server: {name}")
    elif entity_type == "component":
        COMPONENT_REGISTRY[name] = entry
        logger.info(f"Registered component: {name}")
    else:
        raise ValueError("Entity type must be 'server' or 'component'")

def unregister_entity(name: str, entity_type: EntityType) -> bool:
    """Remove entity from registry. Returns True if successful."""
    if entity_type == "server":
        if name in SERVER_REGISTRY:
            del SERVER_REGISTRY[name]
            logger.info(f"Unregistered SOVD server: {name}")
            return True
    elif entity_type == "component":
        if name in COMPONENT_REGISTRY:
            del COMPONENT_REGISTRY[name]
            logger.info(f"Unregistered component: {name}")
            return True
    else:
        raise ValueError("Entity type must be 'server' or 'component'")
    return False

def get_registry() -> Dict[str, Dict[str, Any]]:
    """Get complete registry with servers and components."""
    return {"servers": SERVER_REGISTRY, "components": COMPONENT_REGISTRY}

def get_server_info(name: str) -> Optional[Dict[str, Any]]:
    """Get registered SOVD server info by name."""
    return SERVER_REGISTRY.get(name)

def get_all_servers() -> Dict[str, Dict[str, Any]]:
    return SERVER_REGISTRY.copy()
