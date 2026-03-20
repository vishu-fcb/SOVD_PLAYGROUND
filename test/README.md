# SOVD Tests

pytest test suite for SOVD Gateway and applications.

## Quick Start

**Install dependencies:**

```bash
pip install pytest requests
```

**Start services:**

```bash
cd hpc/sovd
docker compose up -d
```

**Run tests:**

```bash
pytest test/
```

## Test Files

| File                        | Target                | Description                          |
| --------------------------- | --------------------- | ------------------------------------ |
| `test_ac_control.py`        | AC Control App        | Logs, config, data, operations       |
| `test_health_monitoring.py` | Health Monitoring App | System health, processes, filesystem |
| `test_light_control.py`     | Light Control App     | Lights data, operations              |
| `test_mcp_server.py`        | MCP Server            | Health, discovery, endpoints         |

## Test Coverage

### AC Control

- GET/POST logs
- GET/PUT configuration
- GET/PUT data items
- GET faults
- GET/POST operations

### Health Monitoring

- System health metrics
- Process list
- Filesystem info

### Light Control

- Light data items
- Toggle operations
- All on/off operations

### MCP Server

- Health check
- Server discovery
- Endpoint mapping

## Usage

**Run all tests:**

```bash
pytest test/
```

**Run specific file:**

```bash
pytest test/test_ac_control.py
```

**Run with verbose output:**

```bash
pytest test/ -v
```

**Run specific test:**

```bash
pytest test/test_ac_control.py::test_get_ac_logs -v
```

## Configuration

Tests use unprotected internal ports:

- Gateway: `http://localhost:7660`
- MCP Server: `http://localhost:7693`

For testing with authentication (port 8080), modify `BASE_URL` and add JWT token headers.

## Adding Tests

Create new test file in `test/`:

```python
import pytest
import requests

BASE_URL = "http://localhost:7660"
APP_PREFIX = "/app/my-app"

def test_my_endpoint():
    response = requests.get(f"{BASE_URL}{APP_PREFIX}/endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_key" in data
```

Follow naming convention: `test_*.py` with `test_*()` functions.
