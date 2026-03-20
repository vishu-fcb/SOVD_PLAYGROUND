"""Router management for SOVD server."""

import inspect
import logging
from typing import Dict, Any, List, Callable, Optional

from fastapi import FastAPI, APIRouter, Request, Path, Query, Body
from fastapi.routing import APIRoute
from pydantic import BaseModel, create_model

from infrastructure.registry import get_all_servers
from infrastructure.proxy import proxy_request_for_app
from infrastructure.openapi_handler import openapi_handler

logger = logging.getLogger(__name__)

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

# Track created routers to avoid duplicates
created_routers = set()
included_routers = set()

async def create_app_routers(app_instance: FastAPI):
    """Generate routers for all registered apps."""
    apps = get_all_servers()

    for app_name, app_info in apps.items():
        if app_name not in created_routers:
            await create_app_router(app_instance, app_name, app_info)
            created_routers.add(app_name)

async def create_app_router(app_instance: FastAPI, app_name: str, app_info: Dict[str, Any]):
    """Generate router for a single app."""
    try:
        # Get app metadata
        metadata = app_info.get("metadata", {})
        app_title = metadata.get("title", app_name.replace('-', ' ').title())

        # Check if we have OpenAPI spec
        service_spec = openapi_handler.service_specs.get(app_name)

        if not service_spec:
            logger.warning(f"No OpenAPI spec found for {app_name}")
            return

        # Create router with tag
        tag_name = f"{app_title} ({app_name})"
        app_router = APIRouter(tags=[tag_name])

        # Create routes for each path in the service spec
        paths = service_spec.get("paths", {})
        for path, path_spec in paths.items():
            # Pass original service path to _create_routes_for_path
            # Function handles adding /app/{app_name} prefix internally
            _create_routes_for_path(app_router, app_name, app_title, path, path_spec, service_spec)

        # Include the router if not already included
        if app_name not in included_routers:
            app_instance.include_router(app_router)
            included_routers.add(app_name)
            logger.info(f"Created router for app: {app_name}")

        # Clear cached OpenAPI to force regeneration
        app_instance.openapi_schema = None

    except Exception as e:
        logger.error(f"Error creating router for {app_name}: {e}")

def _create_routes_for_path(
    router: APIRouter,
    app_name: str,
    app_title: str,
    path: str,
    path_spec: Dict[str, Any],
    service_spec: Dict[str, Any]
):
    """Add routes for HTTP methods to router."""
    path_sanitized = path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')

    for method, method_spec in path_spec.items():
        if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options']:
            continue

        # Generate unique operation ID to avoid conflicts
        operation_id = f"{app_name}_{method.lower()}_{path_sanitized}"
        summary = method_spec.get("summary", f"{method.upper()} {path}")
        description = method_spec.get("description", f"{method.upper()} endpoint from {app_title}")

        # Extract parameters from OpenAPI spec
        parameters = method_spec.get("parameters", [])
        request_body = method_spec.get("requestBody", {})

        # Create dynamic function with proper FastAPI parameter annotations
        def create_dynamic_route_handler(
            current_app_name: str,
            service_path: str,
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
                    
                    model_name = schema_name if schema_name else f"{current_app_name}RequestBody"
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
                # Extract path parameters and substitute them in the service path
                actual_service_path = service_path

                # Remove 'body' from kwargs since it's handled separately by FastAPI
                body_data = kwargs.pop('body', None)

                # Replace path parameters in service path using kwargs
                for param_name, param_value in kwargs.items():
                    if param_value is not None:
                        actual_service_path = actual_service_path.replace(f"{{{param_name}}}", str(param_value))

                return await proxy_request_for_app(request, current_app_name, actual_service_path)

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

        # Router path includes /app/{app_name} prefix
        # Service path is original path from service's OpenAPI spec
        service_path = path
        router_path = f"/app/{app_name}{path}"

        # Extract and process responses from the method spec
        responses = method_spec.get("responses", {})
        openapi_handler._update_schema_refs_recursive(responses, app_name)

        # Default responses can be merged with the service's responses
        default_responses = {
            404: {"description": "App not found"},
            502: {"description": "Bad gateway"},
            504: {"description": "Gateway timeout"}
        }
        merged_responses = {**responses, **default_responses}

        router.add_api_route(
            router_path,
            create_dynamic_route_handler(
                app_name,
                service_path,
                parameters,
                request_body,
                service_spec.get("components", {})
            ),
            methods=[method.upper()],
            summary=f"[{app_name}] {summary}",
            description=description,
            operation_id=operation_id,
            responses=merged_responses
        )
