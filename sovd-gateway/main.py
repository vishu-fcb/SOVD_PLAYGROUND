"""
SOVD Gateway - Service Oriented Vehicle Diagnostics Gateway
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from infrastructure.registry import register_entity, get_all_servers, get_server_info
from infrastructure.openapi_handler import openapi_handler
from infrastructure.router_manager import create_server_router, created_routers, endpoint_mapping
from schemas import (
    DiscoveryResponse, RegistrationResponse, ServersListResponse,
    EndpointMappingResponse, RefreshResponse, HealthResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServerRegistration(BaseModel):
    """Model for server registration data."""
    name: str
    url: str
    type: str = "server"
    metadata: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    logger.info("SOVD Gateway starting up...")
    logger.info("Use /discover endpoint to fetch and merge SOVD server APIs")
    yield
    logger.info("SOVD Gateway shutting down...")


app = FastAPI(
    title="SOVD Gateway",
    version="1.0.0",
    description=(
        "Service Oriented Vehicle Diagnostics Gateway - 1:1 mapping of service endpoints. "
        "Use /discover to fetch services from SOVD servers."
    ),
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


async def fetch_and_merge_server_openapi(server_name: str, server_url: str):
    """Fetch and merge server OpenAPI spec and create router."""
    spec = await openapi_handler.fetch_server_openapi(server_name, server_url)
    if spec:
        server_info = get_server_info(server_name)
        if server_info:
            # Only create router if not already created
            if server_name not in created_routers:
                await create_server_router(app, server_name, server_info)
                created_routers.add(server_name)
                logger.info(f"OpenAPI schema refreshed and router created for {server_name}")
            else:
                logger.info(f"Router already exists for {server_name}, skipping creation")
        app.openapi_schema = None
    return spec


@app.post("/discover",
    response_model=DiscoveryResponse,
    summary="Discover SOVD servers",
    description="Automatically discovers and registers preconfigured SOVD servers from environment variables. Fetches OpenAPI specifications from each server and creates dynamic routes for accessing their endpoints through the gateway",
    tags=["Server Management"]
)
async def discover_servers():
    """Discover and register SOVD servers from environment configuration."""
    try:
        server_urls = os.getenv("SOVD_SERVER_URLS", "").split(",")
        discovered_servers = []

        for i, url in enumerate(server_urls):
            if url.strip():
                server_name = f"sovd-server-{i+1}"
                logger.info(f"Discovering SOVD server: {server_name} at {url.strip()}")

                register_entity(server_name, "server", {
                    "url": url.strip(),
                    "metadata": {},
                    "status": "discovered"
                })

                spec = await fetch_and_merge_server_openapi(server_name, url.strip())
                if spec:
                    discovered_servers.append({
                        "name": server_name,
                        "url": url.strip(),
                        "status": "successfully_discovered"
                    })
                else:
                    discovered_servers.append({
                        "name": server_name,
                        "url": url.strip(),
                        "status": "discovery_failed"
                    })

        return JSONResponse(
            status_code=200,
            content={
                "message": f"Discovery completed for {len(discovered_servers)} servers",
                "discovered_servers": discovered_servers,
                "docs_url": "/docs"
            }
        )

    except Exception as e:
        logger.error(f"Error during discovery: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Discovery failed: {str(e)}"}
        )

@app.post("/register-server",
    response_model=RegistrationResponse,
    summary="Register SOVD server",
    description="Manually registers a SOVD server with the gateway by providing name and URL. Fetches the server's OpenAPI specification and creates dynamic routes for proxying requests to the server's endpoints",
    tags=["Server Management"]
)
async def register_server(registration_data: ServerRegistration, background_tasks: BackgroundTasks):
    """Register SOVD server and fetch its OpenAPI spec."""
    try:
        server_name = registration_data.name
        server_url = registration_data.url
        entity_type = registration_data.type

        logger.info(f"Registering SOVD server: {server_name} at {server_url}")

        # Register the server
        register_entity(server_name, entity_type, {
            "url": server_url,
            "metadata": registration_data.metadata,
            "status": "registered"
        })

        # Fetch OpenAPI spec in background
        background_tasks.add_task(fetch_and_merge_server_openapi, server_name, server_url)

        return JSONResponse(
            status_code=201,
            content={
                "message": f"SOVD server {server_name} registered successfully",
                "name": server_name,
                "url": server_url,
                "type": entity_type
            }
        )

    except Exception as e:
        logger.error(f"Error registering SOVD server: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Registration failed: {str(e)}"}
        )

@app.get("/servers",
    response_model=ServersListResponse,
    summary="List SOVD servers",
    description="Retrieves all registered SOVD servers with their URLs, status, and metadata. Use this to see which backend servers are currently connected to the gateway",
    tags=["Server Management"]
)
async def list_servers():
    """Get all registered SOVD servers."""
    servers = get_all_servers()
    return {
        "servers": servers,
        "count": len(servers)
    }

@app.get("/endpoint-mapping",
    response_model=EndpointMappingResponse,
    summary="Get endpoint mapping",
    description="Shows the current mapping between endpoints and their backend SOVD servers. Use this to understand which server handles each specific endpoint path",
    tags=["Gateway Info"]
)
async def get_endpoint_mapping():
    """Get current endpoint-to-server mapping."""
    return {
        "endpoint_mapping": endpoint_mapping,
        "description": "Shows which server handles each endpoint"
    }

@app.post("/refresh-docs",
    response_model=RefreshResponse,
    summary="Refresh documentation",
    description="Forces a refresh of the OpenAPI documentation by invalidating the cache and regenerating the merged schema from all registered SOVD servers",
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
    description="Returns the gateway's health status, version, and type information for monitoring and service discovery purposes",
    tags=["Health"]
)
def health():
    """Gateway health check."""
    return {"status": "ok", "version": "1.0.0", "type": "gateway"}

@app.get("/status",
    response_model=HealthResponse,
    summary="Status check",
    description="Returns the gateway's status information (alias for /health). Provides status, version, and type for compatibility with different monitoring systems",
    tags=["Health"]
)
def status():
    """Gateway status check (alias for health)."""
    return {"status": "ok", "version": "1.0.0", "type": "gateway"}
