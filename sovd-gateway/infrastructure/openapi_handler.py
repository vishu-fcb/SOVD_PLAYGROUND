"""OpenAPI schema merging for SOVD gateway."""

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

    def __init__(self):
        self.server_specs: Dict[str, Dict[str, Any]] = {}
        self.cached_merged_spec: Optional[Dict[str, Any]] = None

    async def fetch_server_openapi(self, server_name: str, server_url: str) -> Optional[Dict[str, Any]]:
        retries = 5
        delay = 2
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    logger.info(f"Attempt {attempt + 1}/{retries} to fetch OpenAPI from {server_url}/openapi.json")
                    response = await client.get(f"{server_url}/openapi.json")
                    if response.status_code == 200:
                        spec = response.json()
                        self.server_specs[server_name] = spec
                        self.cached_merged_spec = None
                        logger.info(f"Successfully fetched OpenAPI spec for SOVD server {server_name}")
                        return spec
                    else:
                        logger.warning(
                            f"Attempt {attempt + 1} failed to fetch OpenAPI from {server_url}: "
                            f"Status {response.status_code}. Retrying in {delay}s..."
                        )
            except httpx.ConnectError as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed to connect to {server_url}: {e}. "
                    f"Retrying in {delay}s..."
                )

            await asyncio.sleep(delay)

        logger.error(f"All {retries} attempts to fetch OpenAPI from {server_url} failed.")
        return None

    def invalidate_cache(self):
        self.cached_merged_spec = None

    def remove_server_spec(self, server_name: str):
        if server_name in self.server_specs:
            del self.server_specs[server_name]
            self.cached_merged_spec = None
            logger.info(f"Removed OpenAPI spec for SOVD server {server_name}")

    def get_merged_openapi(self, app) -> Dict[str, Any]:
        if self.cached_merged_spec:
            return self.cached_merged_spec

        base_spec = get_openapi(
            title="SOVD Gateway - Unified Service APIs",
            version="1.0.0",
            description=(
                "Service Oriented Vehicle Diagnostics Gateway "
            ),
            routes=app.routes,
        )

        if self.server_specs:
            base_spec.setdefault("components", {}).setdefault("schemas", {})

            for server_name, server_spec in self.server_specs.items():
                self._merge_component_schemas(base_spec, server_spec, server_name)

        self.cached_merged_spec = base_spec
        return base_spec

    def _merge_component_schemas(self, merged_spec: Dict[str, Any], server_spec: Dict[str, Any], server_name: str):
        if "components" in server_spec and "schemas" in server_spec["components"]:
            for schema_name, schema_def in server_spec["components"]["schemas"].items():
                prefix = server_name.replace('-', '_').replace(' ', '_')
                prefixed_name = f"{prefix}_{schema_name}"

                schema_copy = copy.deepcopy(schema_def)
                self._update_schema_refs_recursive(schema_copy, server_name)
                merged_spec["components"]["schemas"][prefixed_name] = schema_copy

    def _update_schema_refs_recursive(self, obj: Any, server_name: str) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str) and value.startswith(SCHEMA_REF_PREFIX):
                    try:
                        original_ref = value.split("/")[-1]
                        if original_ref:
                            prefix = server_name.replace('-', '_').replace(' ', '_')
                            prefixed_ref = f"{SCHEMA_REF_PREFIX}{prefix}_{original_ref}"
                            obj[key] = prefixed_ref
                    except (IndexError, AttributeError):
                        pass
                else:
                    self._update_schema_refs_recursive(value, server_name)
        elif isinstance(obj, list):
            for item in obj:
                self._update_schema_refs_recursive(item, server_name)


openapi_handler = OpenAPIHandler()
