import pytest
import requests

# The base URL for the SOVD Gateway, now using the unprotected internal port
BASE_URL = "http://localhost:7660"

# Define the server prefix for the light-control app
APP_PREFIX = "/app/light-control"

def test_get_light_logs():
    """
    Tests fetching the logs for the light control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)

def test_post_light_log():
    """
    Tests adding a new log entry to the light control application.
    """
    log_entry = {"event": "Test log entry for light control from pytest"}
    response = requests.post(f"{BASE_URL}{APP_PREFIX}/logs", json=log_entry)
    assert response.status_code == 200
    data = response.json()
    assert data["event"] == log_entry["event"]

def test_get_light_configuration():
    """
    Tests fetching the configuration of the light control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/configuration")
    assert response.status_code == 200
    data = response.json()
    assert "configuration" in data
    assert isinstance(data["configuration"], dict)

def test_update_light_configuration():
    """
    Tests updating a configuration key in the light control application.
    """
    # This key might need to be adjusted based on the actual available configurations
    config_key = "brightness"
    config_value = 80
    
    # Check if the key exists before trying to update it
    config_response = requests.get(f"{BASE_URL}{APP_PREFIX}/configuration")
    if config_key not in config_response.json().get("configuration", {}):
        pytest.skip(f"Configuration key '{config_key}' not found.")

    response = requests.put(f"{BASE_URL}{APP_PREFIX}/configuration/{config_key}", json={"value": config_value})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["key"] == config_key
    assert data["value"] == config_value

def test_get_light_data_items():
    """
    Tests fetching all data items from the light control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/data")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_light_data_item_by_id():
    """
    Tests fetching a single data item by its ID from the light control application.
    """
    all_items_response = requests.get(f"{BASE_URL}{APP_PREFIX}/data")
    assert all_items_response.status_code == 200
    items = all_items_response.json().get("items", [])
    if not items:
        pytest.skip("No data items found to test fetching by ID.")

    item_id = items[0]["id"]
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/data/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id

def test_update_light_data_item():
    """
    Tests updating a data item in the light control application.
    """
    all_items_response = requests.get(f"{BASE_URL}{APP_PREFIX}/data")
    assert all_items_response.status_code == 200
    items = all_items_response.json().get("items", [])
    if not items:
        pytest.skip("No data items found to test updating.")

    item_id = items[0]["id"]
    # Assuming the data item can be updated with a 'state'
    update_payload = {"data": {"state": True}}
    response = requests.put(f"{BASE_URL}{APP_PREFIX}/data/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["state"] is True

def test_get_light_faults():
    """
    Tests fetching the faults from the light control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/faults")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_light_operations():
    """
    Tests fetching the available operations for the light control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations")
    assert response.status_code == 200
    data = response.json()
    assert "operations" in data
    assert isinstance(data["operations"], list)

def test_execute_light_operation():
    """
    Tests executing a light control operation.
    """
    operations_response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations")
    assert operations_response.status_code == 200
    operations = operations_response.json().get("operations", [])
    if not operations:
        pytest.skip("No operations found to test execution.")

    operation_id = operations[0]["id"]
    execution_response = requests.post(f"{BASE_URL}{APP_PREFIX}/operations/{operation_id}/executions", json={"parameters": {}})
    assert execution_response.status_code == 200
    execution_data = execution_response.json()
    assert "id" in execution_data
    assert "status" in execution_data
