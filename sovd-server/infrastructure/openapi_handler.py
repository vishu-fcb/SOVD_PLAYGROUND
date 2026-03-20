"""OpenAPI schema merging for SOVD server API documentation."""

import asyncio
import copy
import httpx
import logging
from typing import Dict, Any, Optional

from fastapi.openapi.utils import get_openapi

logger = logging.getLogger(__name__)

# Constants
SCHEMA_REF_PREFIX = "#/components/schemas/"


class OpenAPIHandler:
    """Merges OpenAPI specifications from registered services."""

    def __init__(self):
        self.service_specs: Dict[str, Dict[str, Any]] = {}
        self.cached_merged_spec: Optional[Dict[str, Any]] = None

    async def fetch_service_openapi(self, service_name: str, service_url: str) -> Optional[Dict[str, Any]]:
        """Fetch OpenAPI spec with retries."""
        retries = 5
        delay = 2  # seconds
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    logger.info(f"Attempt {attempt + 1}/{retries} to fetch OpenAPI from {service_url}/openapi.json")
                    response = await client.get(f"{service_url}/openapi.json")
                    if response.status_code == 200:
                        spec = response.json()
                        self.service_specs[service_name] = spec
                        self.cached_merged_spec = None  # Invalidate cache
                        logger.info(f"Successfully fetched OpenAPI spec for {service_name}")
                        return spec
                    else:
                        logger.warning(
                            f"Attempt {attempt + 1} failed to fetch OpenAPI from {service_url}: "
                            f"Status {response.status_code}. Retrying in {delay}s..."
                        )
            except httpx.ConnectError as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed to connect to {service_url}: {e}. "
                    f"Retrying in {delay}s..."
                )

            await asyncio.sleep(delay)

        logger.error(f"All {retries} attempts to fetch OpenAPI from {service_url} failed.")
        return None

    def invalidate_cache(self):
        """Reset cached spec to force regeneration."""
        self.cached_merged_spec = None

    def remove_service_spec(self, service_name: str):
        """Remove service spec and invalidate cache."""
        if service_name in self.service_specs:
            del self.service_specs[service_name]
            self.cached_merged_spec = None  # Invalidate cache
            logger.info(f"Removed OpenAPI spec for {service_name}")

    def get_merged_openapi(self, app) -> Dict[str, Any]:
        """Generate unified OpenAPI schema with dynamic routes."""
        if self.cached_merged_spec:
            return self.cached_merged_spec

        # Generate schema from FastAPI app which now includes all dynamic routes
        base_spec = get_openapi(
            title="SOVD Server - Unified Services",
            version="1.0.0",
            description="Service Oriented Vehicle Diagnostics Server with registered service APIs",
            routes=app.routes,
        )

        # Merge component schemas from registered services
        if self.service_specs:
            base_spec.setdefault("components", {}).setdefault("schemas", {})

            for service_name, service_spec in self.service_specs.items():
                self._merge_component_schemas(base_spec, service_spec, service_name)

        self.cached_merged_spec = base_spec
        return base_spec

    def _merge_component_schemas(self, merged_spec: Dict[str, Any], service_spec: Dict[str, Any], service_name: str):
        """Merge schemas using prefixed names to avoid conflicts."""
        if "components" in service_spec and "schemas" in service_spec["components"]:
            for schema_name, schema_def in service_spec["components"]["schemas"].items():
                # Use service_name for unique prefixing
                prefix = service_name.replace('-', '_').replace(' ', '_')
                prefixed_name = f"{prefix}_{schema_name}"

                schema_copy = copy.deepcopy(schema_def)
                self._update_schema_refs_recursive(schema_copy, service_name)
                merged_spec["components"]["schemas"][prefixed_name] = schema_copy

    def _update_schema_refs_recursive(self, obj: Any, service_name: str) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str) and value.startswith(SCHEMA_REF_PREFIX):
                    try:
                        original_ref = value.split("/")[-1]
                        if original_ref:
                            prefix = service_name.replace('-', '_').replace(' ', '_')
                            prefixed_ref = f"{SCHEMA_REF_PREFIX}{prefix}_{original_ref}"
                            obj[key] = prefixed_ref
                    except (IndexError, AttributeError):
                        pass
                else:
                    self._update_schema_refs_recursive(value, service_name)
        elif isinstance(obj, list):
            for item in obj:
                self._update_schema_refs_recursive(item, service_name)


openapi_handler = OpenAPIHandler()
