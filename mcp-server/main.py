import httpx
import logging
import os
import json

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOVD_GW_URL = os.getenv("SOVD_GW_URL", "http://sovd-gateway:7690")
MCP_LOCAL_OPENAPI = os.getenv("MCP_LOCAL_OPENAPI", "false").lower() in ('true', '1', 't')

# HTTP client for the SOVD Gateway
client = httpx.AsyncClient(base_url=SOVD_GW_URL)

openapi_spec = None

if MCP_LOCAL_OPENAPI:
    logger.info("MCP_LOCAL_OPENAPI is true, loading openapi.json from file")
    # Load OpenAPI spec from a local file
    with open("openapi.json", "r") as f:
        openapi_spec = json.load(f)
else:
    logger.info("MCP_LOCAL_OPENAPI is false, fetching openapi.json from SOVD Gateway")
    # Load OpenAPI spec from the gateway
    openapi_spec = httpx.get(f"{SOVD_GW_URL}/openapi.json").json()


# Create the MCP server from the OpenAPI spec
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="SOVD Gateway MCP Server"
)

if __name__ == "__main__":
    import uvicorn
    app = mcp.http_app(path="/mcp")
    uvicorn.run(app, host="0.0.0.0", port=7693)
