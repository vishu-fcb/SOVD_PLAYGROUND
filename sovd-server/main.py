"""
SOVD Server - Service Oriented Vehicle Diagnostics Server
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from infrastructure.registry import register_entity, get_all_servers, get_server_info
from infrastructure.openapi_handler import openapi_handler
from infrastructure.router_manager import create_app_router
from schemas import (
    RegistrationDebugResponse, RegistrationResponse, ServicesListResponse,
    RefreshResponse, HealthResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceRegistration(BaseModel):
    """Model for service registration data."""
    name: str
    url: str
    type: str = "app"
    endpoints: List[Dict[str, Any]]
    metadata: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    logger.info("SOVD Server starting up...")
    yield
    logger.info("SOVD Server shutting down...")


app = FastAPI(
    title="SOVD Server",
    version="1.0.0",
    description="Service Oriented Vehicle Diagnostics Server with Dynamic Service Registration",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    """Generate custom merged OpenAPI schema."""
    return openapi_handler.get_merged_openapi(app)


app.openapi = custom_openapi


async def fetch_and_merge_service_openapi(service_name: str, service_url: str):
    """Fetch and merge service OpenAPI spec and create router."""
    await openapi_handler.fetch_service_openapi(service_name, service_url)
    app_info = get_server_info(service_name)
    if app_info:
        await create_app_router(app, service_name, app_info)
    app.openapi_schema = None
    logger.info(f"OpenAPI schema refreshed and router created for {service_name}")

@app.post("/register-debug",
    response_model=RegistrationDebugResponse,
    summary="Debug registration endpoint",
    description="Debug endpoint for logging and inspecting service registration payloads. Used for troubleshooting registration issues and validating request formats",
    tags=["Debug"]
)
async def register_debug(request: Request):
    body = await request.json()
    logger.info(f"DEBUG PAYLOAD RECEIVED: {body}")
    return {"status": "payload logged"}

@app.post("/register",
    response_model=RegistrationResponse,
    summary="Register service",
    description="Registers a new vehicle service (SOVD application) with the server by providing service details and endpoints. Automatically fetches the service's OpenAPI specification and creates dynamic routes for accessing the service",
    tags=["Service Management"]
)
async def register_service(registration_data: ServiceRegistration, background_tasks: BackgroundTasks):
    try:
        service_name = registration_data.name
        service_url = registration_data.url
        entity_type = registration_data.type

        logger.info(f"Registering service: {service_name} at {service_url}")

        register_entity(service_name, entity_type, {
            "url": service_url,
            "metadata": registration_data.metadata,
            "status": "registered"
        })

        if entity_type == "app":
            background_tasks.add_task(fetch_and_merge_service_openapi, service_name, service_url)

        return JSONResponse(
            status_code=201,
            content={
                "message": f"Service {service_name} registered successfully",
                "name": service_name,
                "url": service_url,
                "type": entity_type
            }
        )

    except Exception as e:
        logger.error(f"Error registering service: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Registration failed: {str(e)}"}
        )

@app.get("/services",
    response_model=ServicesListResponse,
    summary="List services",
    description="Retrieves all registered vehicle services with their URLs, endpoints, and metadata. Use this to discover available SOVD applications and their capabilities",
    tags=["Service Management"]
)
async def list_services():
    """Get all registered services."""
    apps = get_all_servers()
    return {
        "services": apps,
        "count": len(apps)
    }

@app.post("/refresh-docs",
    response_model=RefreshResponse,
    summary="Refresh documentation",
    description="Forces a refresh of the OpenAPI documentation by invalidating the cache and regenerating the merged schema from all registered vehicle services",
    tags=["Documentation"]
)
async def refresh_docs():
    """Force OpenAPI documentation refresh."""
    openapi_handler.invalidate_cache()
    app.openapi_schema = None
    return {"message": "OpenAPI documentation refreshed"}

@app.get("/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the SOVD server's health status and version information for monitoring and service discovery purposes",
    tags=["Health"]
)
def health():
    """Server health check."""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/status",
    response_model=HealthResponse,
    summary="Status check",
    description="Returns the SOVD server's status information (alias for /health). Provides status and version for compatibility with different monitoring systems",
    tags=["Health"]
)
def status():
    """Server status check (alias for health)."""
    return {"status": "ok", "version": "1.0.0"}
