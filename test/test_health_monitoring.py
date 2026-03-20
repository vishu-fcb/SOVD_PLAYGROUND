import pytest
import requests

# The base URL for the SOVD Gateway, now using the unprotected internal port
BASE_URL = "http://localhost:7660"

# Define the server prefix for the health-monitoring app
APP_PREFIX = "/app/health-monitoring"

def test_get_health_metrics():
    """
    Tests fetching the system health metrics.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/health")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "cpu" in data
    assert "memory" in data

def test_get_running_processes():
    """
    Tests fetching the list of running processes.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/proc")
    assert response.status_code == 200
    data = response.json()
    assert "processes" in data
    assert isinstance(data["processes"], list)

def test_get_process_details():
    """
    Tests fetching details for a specific process.
    """
    # First, get all processes to find a valid PID (use PID 1, which should always exist)
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/proc/1")
    assert response.status_code == 200
    data = response.json()
    assert data["pid"] == 1
    assert "name" in data

def test_get_network_interfaces():
    """
    Tests fetching network interface information.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/net")
    assert response.status_code == 200
    data = response.json()
    assert "interfaces" in data
    assert isinstance(data["interfaces"], dict)

def test_get_filesystem_info():
    """
    Tests fetching filesystem information.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/fs")
    assert response.status_code == 200
    data = response.json()
    assert "filesystems" in data
    assert isinstance(data["filesystems"], list)
