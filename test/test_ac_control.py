import pytest
import requests

# The base URL for the SOVD Gateway, now using the unprotected internal port
BASE_URL = "http://localhost:7660"

# Define the server prefix for the ac-control app
APP_PREFIX = "/app/ac-control"

def test_get_ac_logs():
    """
    Tests fetching the logs for the AC control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)

def test_post_ac_log():
    """
    Tests adding a new log entry to the AC control application.
    """
    log_entry = {"event": "Test log entry from pytest"}
    response = requests.post(f"{BASE_URL}{APP_PREFIX}/logs", json=log_entry)
    assert response.status_code == 200
    data = response.json()
    assert data["event"] == log_entry["event"]

def test_get_ac_configuration():
    """
    Tests fetching the configuration of the AC control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/configuration")
    assert response.status_code == 200
    data = response.json()
    assert "configuration" in data
    assert isinstance(data["configuration"], dict)

def test_update_ac_configuration():
    """
    Tests updating a configuration key in the AC control application.
    """
    config_key = "Mode"
    config_value = "eco"
    response = requests.put(f"{BASE_URL}{APP_PREFIX}/configuration/{config_key}", json={"value": config_value})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    assert data["key"] == config_key
    assert data["value"] == config_value

def test_get_ac_data_items():
    """
    Tests fetching all data items from the AC control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/data")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_ac_data_item_by_id():
    """
    Tests fetching a single data item by its ID from the AC control application.
    """
    # First, get all items to find a valid ID
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

def test_update_ac_data_item():
    """
    Tests updating a data item in the AC control application.
    """
    all_items_response = requests.get(f"{BASE_URL}{APP_PREFIX}/data")
    assert all_items_response.status_code == 200
    items = all_items_response.json().get("items", [])
    if not items:
        pytest.skip("No data items found to test updating.")

    item_id = items[0]["id"]
    update_payload = {"data": {"FanSpeed": 5}}
    response = requests.put(f"{BASE_URL}{APP_PREFIX}/data/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["FanSpeed"] == 5

def test_get_ac_faults():
    """
    Tests fetching the faults from the AC control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/faults")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_ac_operations():
    """
    Tests fetching the available operations for the AC control application.
    """
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations")
    assert response.status_code == 200
    data = response.json()
    assert "operations" in data
    assert isinstance(data["operations"], list)

def test_get_ac_operation_description():
    """
    Tests fetching the description of a single operation.
    """
    operations_response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations")
    assert operations_response.status_code == 200
    operations = operations_response.json().get("operations", [])
    if not operations:
        pytest.skip("No operations found to test fetching descriptions.")

    operation_id = operations[0]["id"]
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations/{operation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == operation_id

def test_execute_ac_operation():
    """
    Tests executing an operation and checking its status.
    """
    operations_response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations")
    assert operations_response.status_code == 200
    operations = operations_response.json().get("operations", [])
    if not operations:
        pytest.skip("No operations found to test execution.")

    operation_id = operations[0]["id"]
    # Assuming the first operation requires no parameters for simplicity
    execution_response = requests.post(f"{BASE_URL}{APP_PREFIX}/operations/{operation_id}/executions", json={"parameters": {}})
    assert execution_response.status_code == 200
    execution_data = execution_response.json()
    assert "id" in execution_data
    assert "status" in execution_data

    execution_id = execution_data["id"]
    status_response = requests.get(f"{BASE_URL}{APP_PREFIX}/operations/{operation_id}/executions/{execution_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == execution_id
