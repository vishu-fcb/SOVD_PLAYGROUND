import pytest
import requests

# The base URL for the SOVD Gateway, now using the unprotected internal port
BASE_URL = "http://localhost:7693"
MCP_SERVER_URL = "http://localhost:7693"

def test_health_check():
    """
    Tests the /health endpoint of the MCP server.

    This endpoint is used to verify that the MCP server is running and healthy.
    It should return a 200 OK status code and a JSON object with the server's status.
    """
    response = requests.get(f"{MCP_SERVER_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_list_servers():
    """
    Tests the /servers endpoint of the MCP server.

    This endpoint lists all the SOVD servers that are registered with the SOVD gateway.
    This is useful for discovering what services are available.
    """
    response = requests.get(f"{MCP_SERVER_URL}/servers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Add more specific assertions based on expected servers if known

def test_get_endpoint_mapping():
    """
    Tests the /endpoint-mapping endpoint of the MCP server.

    This endpoint shows how the API gateway routes requests to the backend SOVD servers.
    It's a crucial endpoint for understanding the API structure.
    """
    response = requests.get(f"{MCP_SERVER_URL}/endpoint-mapping")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_discover_servers():
    """
    Tests the /discover endpoint of the MCP server.

    This endpoint triggers the automatic discovery of SOVD servers.
    This is a POST request that should initiate a discovery process.
    """
    response = requests.post(f"{MCP_SERVER_URL}/discover")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "details" in data

def test_refresh_docs():
    """
    Tests the /refresh-docs endpoint of the MCP server.

    This endpoint forces the gateway to refresh its OpenAPI documentation from all registered servers.
    This is useful when a service has been updated.
    """
    response = requests.post(f"{MCP_SERVER_URL}/refresh-docs")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Documentation cache invalidated and regenerated."

# To run these tests, you will need to install pytest and requests:
# pip install pytest requests
# Then, from the 'sovd' directory, run:
# pytest test/
