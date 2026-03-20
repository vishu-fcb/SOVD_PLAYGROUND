"""Router management for SOVD gateway."""

import copy
import inspect
import logging
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Request, Path, Query, Body
from fastapi.routing import APIRoute
from pydantic import create_model

from infrastructure.registry import get_all_servers
from infrastructure.proxy import proxy_request_for_server
from infrastructure.openapi_handler import openapi_handler

logger = logging.getLogger(__name__)

# Constants
SCHEMA_REF_PREFIX = "#/components/schemas/"
DEFAULT_ERROR_RESPONSES = {
    "404": {"description": "Service not found"},
    "502": {"description": "Bad gateway"},
    "504": {"description": "Gateway timeout"}
}

# Track created routers to avoid duplicates
created_routers = set()
included_routers = set()

# Global endpoint-to-server mapping
endpoint_mapping: Dict[str, Dict[str, str]] = {}  # {method: {path: server_name}}

def clear_router_cache():
    """Clear all router tracking data. Useful for testing or resetting the gateway."""
    global created_routers, included_routers, endpoint_mapping
    created_routers.clear()
    included_routers.clear()
    endpoint_mapping.clear()
    logger.info("Router cache cleared")

def get_server_for_endpoint(method: str, path: str) -> str:
    """Get the server name that handles a specific endpoint"""
    return endpoint_mapping.get(method.upper(), {}).get(path)

def _generate_semantic_operation_id(path: str, method: str) -> str:
    """
    Generate a semantic operation ID from the path and method.
    
    Pattern: {action}_{app_name}_{resource}
    
    Examples:
        /app/ac-control/logs + GET -> get_ac_control_logs
        /app/ac-control/logs + POST -> add_ac_control_log
        /app/light-control/data/{item_id} + GET -> get_light_control_data_item
        /app/light-control/data/{item_id} + PUT -> update_light_control_data_item
        /app/ac-control/configuration/{key} + PUT -> update_ac_control_configuration
        /app/ac-control/faults/{code} + DELETE -> delete_ac_control_fault
        /app/ac-control/operations/{operation_id}/executions + POST -> execute_ac_control_operation
        /app/ac-control/operations/{operation_id}/executions/{execution_id} + GET -> get_ac_control_operation_execution
    
    See docs/api/MCP_TOOL_NAMING.md for complete documentation.
    """
    # Remove /app/ prefix and split path
    path_clean = path.replace('/app/', '').strip('/')
    parts = path_clean.split('/')
    
    # Extract app name (e.g., 'ac-control', 'light-control', 'health-monitoring')
    app_name = parts[0] if parts else 'unknown'
    
    # Replace hyphens with underscores
    app_name_clean = app_name.replace('-', '_')
    
    # Build resource path (everything after app name)
    resource_parts = parts[1:] if len(parts) > 1 else []
    
    # Handle path parameters
    resource_clean = []
    for part in resource_parts:
        if part.startswith('{') and part.endswith('}'):
            # Convert {item_id} to 'item', {code} to 'code', etc.
            param_name = part.strip('{}').replace('_id', '').replace('_', '')
            resource_clean.append(param_name if param_name else 'item')
        else:
            resource_clean.append(part.replace('-', '_'))
    
    resource_name = '_'.join(resource_clean) if resource_clean else ''
    
    # Special case: simplify operations/executions patterns
    # /app/ac-control/operations/{operation_id}/executions -> execute_ac_control_operation
    if 'operations' in resource_clean and 'executions' in resource_clean:
        resource_name = 'operation'
    elif resource_name.endswith('_executions_execution'):
        # /operations/{operation_id}/executions/{execution_id} -> operation_execution
        resource_name = 'operation_execution'
    
    # Map HTTP methods to action prefixes
    action_map = {
        'get': 'get',
        'post': 'execute' if resource_name == 'operation' else 'add' if 'log' in resource_name else 'create',
        'put': 'update',
        'patch': 'update',
        'delete': 'delete'
    }
    
    action = action_map.get(method.lower(), method.lower())
    
    # Build final operation ID
    if resource_name:
        operation_id = f"{action}_{app_name_clean}_{resource_name}"
    else:
        operation_id = f"{action}_{app_name_clean}"
    
    # Handle plural/singular for logs
    if resource_name == 'logs' and method.lower() == 'post':
        operation_id = f"add_{app_name_clean}_log"
    
    return operation_id

async def create_server_routers(app_instance: FastAPI):
    """Generate routers for all registered SOVD servers."""
    servers = get_all_servers()

    for server_name, server_info in servers.items():
        if server_name not in created_routers:
            await create_server_router(app_instance, server_name, server_info)
            created_routers.add(server_name)

async def create_server_router(app_instance: FastAPI, server_name: str, server_info: Dict[str, Any]):
    """Generate router for a single SOVD server with 1:1 path mapping."""
    try:
        # Get server metadata
        metadata = server_info.get("metadata", {})
        server_title = metadata.get("title", server_name.replace('-', ' ').title())

        # Check if we have OpenAPI spec
        server_spec = openapi_handler.server_specs.get(server_name)

        if not server_spec:
            logger.warning(f"No OpenAPI spec found for SOVD server {server_name}")
            return

        # Create routes for each path in the server spec
        paths = server_spec.get("paths", {})
        for path, path_spec in paths.items():
            _create_routes_for_path(app_instance, server_name, server_title, path, path_spec, server_spec)

        logger.info(f"Created 1:1 path mapping for SOVD server: {server_name}")

        # Clear cached OpenAPI to force regeneration
        app_instance.openapi_schema = None

    except Exception as e:
        logger.error(f"Error creating router for SOVD server {server_name}: {e}")

def _create_routes_for_path(
    app_instance: FastAPI,
    server_name: str,
    server_title: str,
    path: str,
    path_spec: Dict[str, Any],
    server_spec: Dict[str, Any]
):
    """Add routes directly to the app with original paths (1:1 mapping)."""

    # Skip server-level endpoints to avoid conflicts and focus only on app endpoints
    server_level_paths = ['/register', '/register-debug', '/services', '/refresh-docs', '/health']
    if path in server_level_paths:
        logger.info(f"Skipping server-level endpoint: {path} from {server_name}")
        return

    # Only process app-level endpoints that start with /app/
    if not path.startswith('/app/'):
        logger.info(f"Skipping non-app endpoint: {path} from {server_name}")
        return

    # Keep the full app path: /app/ac-control/logs
    original_path = path

    path_sanitized = original_path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')

    for method, method_spec in path_spec.items():
        if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options']:
            continue

        # Check if this path+method combination already exists
        method_upper = method.upper()
        existing_server = get_server_for_endpoint(method_upper, original_path)

        if existing_server and existing_server != server_name:
            logger.warning(
                f"Path conflict: {method_upper} {original_path} already mapped to "
                f"{existing_server}, skipping {server_name}"
            )
            continue

        # Add to endpoint mapping
        if method_upper not in endpoint_mapping:
            endpoint_mapping[method_upper] = {}
        endpoint_mapping[method_upper][original_path] = server_name

        # Generate semantic operation ID from path
        # Example: /app/ac-control/logs -> get_ac_control_logs
        # Example: /app/light-control/data/{item_id} -> get_light_control_data_item
        operation_id = _generate_semantic_operation_id(original_path, method.lower())
        
        summary = method_spec.get("summary", f"{method.upper()} {original_path}")
        description = method_spec.get("description", f"{method.upper()} endpoint from {server_title}")

        # Remove server name prefixes from summary if they exist
        if summary.startswith(f"[{server_name}] "):
            summary = summary[len(f"[{server_name}] "):]

        # Extract parameters from OpenAPI spec
        parameters = method_spec.get("parameters", [])
        request_body = method_spec.get("requestBody", {})

        # Create dynamic function with proper FastAPI parameter annotations
        def create_dynamic_route_handler(
            current_server_name: str,
            server_path: str,
            route_parameters: List[Dict[str, Any]],
            request_body_spec: Dict[str, Any],
            openapi_components: Dict[str, Any]
        ):
            # Create parameter annotations for the function
            param_annotations = {}
            param_defaults = {}

            # Add Request parameter (always first)
            param_annotations['request'] = Request

            # Add body parameter if request body is expected
            has_request_body = bool(request_body_spec.get("content"))
            if has_request_body:
                # Try to extract schema information from request body
                content = request_body_spec.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})

                # Create a dynamic Pydantic model based on schema
                body_description = request_body_spec.get("description", "Request body")
                
                # Check if request body is required or has a default
                is_required = request_body_spec.get("required", True)
                has_default = "default" in schema

                if schema:
                    components_schemas = openapi_components.get("schemas", {})

                    schema_name = None
                    resolved_schema = schema
                    if "$ref" in schema:
                        ref_path = schema["$ref"]
                        if ref_path.startswith("#/components/schemas/"):
                            schema_name = ref_path.replace("#/components/schemas/", "")
                            resolved_schema = components_schemas.get(schema_name, schema)
                    
                    openapi_examples = None
                    example_value = None
                    if "examples" in resolved_schema:
                        examples_list = resolved_schema["examples"]
                        if isinstance(examples_list, list) and examples_list:
                            example_value = examples_list[0] if examples_list else None
                            
                            openapi_examples = {}
                            for idx, example in enumerate(examples_list):
                                openapi_examples[f"example_{idx + 1}"] = {
                                    "summary": f"Example {idx + 1}",
                                    "value": example
                                }
                    
                    model_name = schema_name if schema_name else f"{current_server_name}RequestBody"
                    body_model = create_pydantic_model_from_schema(
                        resolved_schema,
                        model_name,
                        components_schemas
                    )
                    param_annotations['body'] = body_model
                    
                    body_kwargs = {
                        "description": body_description,
                        "openapi_examples": openapi_examples
                    }
                    
                    if example_value is not None:
                        body_kwargs["example"] = example_value
                    
                    if has_default or not is_required:
                        param_defaults['body'] = Body(default=None, **body_kwargs)
                    else:
                        param_defaults['body'] = Body(..., **body_kwargs)
                else:
                    # Fallback to Any type
                    param_annotations['body'] = Any
                    if not is_required:
                        param_defaults['body'] = Body(default=None, description=body_description)
                    else:
                        param_defaults['body'] = Body(..., description=body_description)

            # Process route parameters
            for param in route_parameters:
                param_name = param.get("name")
                param_in = param.get("in")
                param_required = param.get("required", True)
                param_description = param.get("description", "")
                param_type = param.get("schema", {}).get("type", "string")

                # Convert OpenAPI type to Python type
                python_type = str  # default
                if param_type == "integer":
                    python_type = int
                elif param_type == "number":
                    python_type = float
                elif param_type == "boolean":
                    python_type = bool

                if param_in == "path":
                    if param_required:
                        param_annotations[param_name] = python_type
                        param_defaults[param_name] = Path(..., description=param_description)
                    else:
                        param_annotations[param_name] = python_type
                        param_defaults[param_name] = Path(None, description=param_description)
                elif param_in == "query":
                    if param_required:
                        param_annotations[param_name] = python_type
                        param_defaults[param_name] = Query(..., description=param_description)
                    else:
                        param_annotations[param_name] = python_type
                        param_defaults[param_name] = Query(None, description=param_description)

            # Create the actual route handler function
            async def route_handler(request: Request, **kwargs):
                # Extract path parameters and substitute them in the server path
                actual_server_path = server_path

                # Remove 'body' from kwargs since it's handled separately by FastAPI
                body_data = kwargs.pop('body', None)

                # Replace path parameters in server path using kwargs
                for param_name, param_value in kwargs.items():
                    if param_value is not None:
                        actual_server_path = actual_server_path.replace(f"{{{param_name}}}", str(param_value))

                return await proxy_request_for_server(request, current_server_name, actual_server_path)

            # Set function annotations and defaults
            route_handler.__annotations__ = param_annotations

            # Create signature with proper defaults
            sig_params = [inspect.Parameter('request', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)]

            for param_name, annotation in param_annotations.items():
                if param_name != 'request':
                    default_value = param_defaults.get(param_name, inspect.Parameter.empty)
                    sig_params.append(
                        inspect.Parameter(
                            param_name,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=annotation,
                            default=default_value
                        )
                    )

            route_handler.__signature__ = inspect.Signature(sig_params)

            return route_handler

        # Use the app path for routing
        server_path = path  # Keep the full original path for server communication
        router_path = original_path  # Use the full app path

        # Extract app name from path for tagging: /app/ac-control/logs -> ac-control
        path_parts = original_path.split('/', 3)
        if len(path_parts) >= 3:
            app_name = path_parts[2]
            tag = f"Application: {app_name}"
        else:
            tag = "Applications"

        # Extract and update response schemas from backend server
        responses = method_spec.get("responses", {})

        # Update schema references in the response
        openapi_handler._update_schema_refs_recursive(responses, server_name)

        # Add default error responses if not present
        merged_responses = {**responses, **DEFAULT_ERROR_RESPONSES}

        # Add route directly to the main app
        # responses dict is used by FastAPI's OpenAPI schema generator
        # The schemas will be included via the merged components from openapi_handler
        app_instance.add_api_route(
            router_path,
            create_dynamic_route_handler(
                server_name,
                server_path,
                parameters,
                request_body,
                server_spec.get("components", {})
            ),
            methods=[method.upper()],
            summary=summary,
            description=f"{description}",
            operation_id=operation_id,
            tags=[tag],
            responses=merged_responses,
            include_in_schema=True
        )

        logger.info(f"Processing path: {path} -> exposed as: {original_path}")
        logger.info(f"Mapped {method_upper} {original_path} -> {server_name} (proxies to {path})")

def create_pydantic_model_from_schema(
    schema: Dict[str, Any],
    model_name: str = "DynamicModel",
    components_schemas: Dict[str, Any] = None
) -> type:
    """Create a Pydantic model from OpenAPI schema."""
    if not schema:
        return dict

    if "$ref" in schema:
        ref_path = schema["$ref"]
        if ref_path.startswith("#/components/schemas/") and components_schemas:
            schema_name = ref_path.replace("#/components/schemas/", "")
            schema = components_schemas.get(schema_name, {})
            if not schema:
                return dict

    schema_type = schema.get("type")
    if schema_type == "object":
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        field_definitions = {}
        for field_name, field_schema in properties.items():
            field_type = _get_python_type_from_schema(field_schema, components_schemas)

            if field_name in required_fields:
                field_definitions[field_name] = (field_type, ...)
            else:
                field_definitions[field_name] = (Optional[field_type], None)

        if field_definitions:
            from pydantic import ConfigDict
            
            config_dict = {}
            if "examples" in schema:
                config_dict["json_schema_extra"] = {"examples": schema["examples"]}
            
            model_config = ConfigDict(**config_dict) if config_dict else None
            created_model = create_model(model_name, **field_definitions)
            
            if model_config:
                created_model.model_config = model_config
            
            return created_model

    return dict

def _get_python_type_from_schema(schema: Dict[str, Any], components_schemas: Dict[str, Any] = None):
    """Convert OpenAPI schema type to Python type."""
    # Resolve $ref if present
    if "$ref" in schema:
        ref_path = schema["$ref"]
        if ref_path.startswith("#/components/schemas/") and components_schemas:
            schema_name = ref_path.replace("#/components/schemas/", "")
            schema = components_schemas.get(schema_name, {})

    # Handle anyOf/oneOf/allOf schemas
    if "anyOf" in schema or "oneOf" in schema:
        # Get the first non-null type from anyOf/oneOf
        alternatives = schema.get("anyOf") or schema.get("oneOf")
        for alt_schema in alternatives:
            if alt_schema.get("type") != "null":
                return _get_python_type_from_schema(alt_schema, components_schemas)
        # If all are null, return Any
        return Any
    elif "allOf" in schema:
        # For allOf, try to use the first schema (simplified handling)
        all_schemas = schema.get("allOf", [])
        if all_schemas:
            return _get_python_type_from_schema(all_schemas[0], components_schemas)
        return Any

    schema_type = schema.get("type")
    
    # If no type is specified, default to Any instead of string
    if not schema_type:
        return Any

    if schema_type == "string":
        return str
    elif schema_type == "integer":
        return int
    elif schema_type == "number":
        return float
    elif schema_type == "boolean":
        return bool
    elif schema_type == "array":
        item_schema = schema.get("items", {})
        item_type = _get_python_type_from_schema(item_schema, components_schemas)
        return List[item_type]
    elif schema_type == "object":
        # For objects with additionalProperties, use Dict[str, Any]
        if schema.get("additionalProperties"):
            return Dict[str, Any]
        else:
            return Dict[str, Any]
    else:
        return Any
