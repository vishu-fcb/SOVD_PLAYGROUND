import logging
from typing import Dict, Any, Optional, Literal, TypedDict

logger = logging.getLogger(__name__)

# Type definitions for better code clarity
EntityType = Literal["app", "component"]

class AppEntry(TypedDict):
    """App registry entry type"""
    url: str
    metadata: Dict[str, Any]
    status: str

class ComponentEntry(TypedDict):
    """Component registry entry type"""
    pass  # Add specific fields as needed

# Registry data stores
APP_REGISTRY: Dict[str, AppEntry] = {}
COMPONENT_REGISTRY: Dict[str, ComponentEntry] = {}

def register_entity(name: str, entity_type: EntityType, entry: Dict[str, Any]) -> None:
    """Register a service or component in the registry."""
    if entity_type == "app":
        APP_REGISTRY[name] = entry
        logger.info(f"Registered app: {name}")
    elif entity_type == "component":
        COMPONENT_REGISTRY[name] = entry
        logger.info(f"Registered component: {name}")
    else:
        raise ValueError("Entity type must be 'app' or 'component'")

def unregister_entity(name: str, entity_type: EntityType) -> bool:
    """Remove entity from registry. Returns True if successful."""
    if entity_type == "app":
        if name in APP_REGISTRY:
            del APP_REGISTRY[name]
            logger.info(f"Unregistered app: {name}")
            return True
    elif entity_type == "component":
        if name in COMPONENT_REGISTRY:
            del COMPONENT_REGISTRY[name]
            logger.info(f"Unregistered component: {name}")
            return True
    else:
        raise ValueError("Entity type must be 'app' or 'component'")
    return False

def get_registry() -> Dict[str, Dict[str, Any]]:
    return {"apps": APP_REGISTRY, "components": COMPONENT_REGISTRY}

def get_server_info(name: str) -> Optional[Dict[str, Any]]:
    return APP_REGISTRY.get(name)

def get_all_servers() -> Dict[str, Dict[str, Any]]:
    return APP_REGISTRY.copy()
