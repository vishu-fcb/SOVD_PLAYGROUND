# SOVD Playground

Service-Oriented Vehicle Diagnostics with FastAPI gateway, service discovery, JWT auth, and OPA policies.

## Quick Start

```bash
docker compose up --build
```

**SOVD Tester:** http://localhost:8085

- Settings → Gateway URL: `http://localhost:8080`
- Public endpoints: `/discover`, `/health`, `/docs`

**Get JWT Token:** http://localhost:8086/docs

### Token Profiles

**Read-Only:**

```json
{
  "user_id": "user:mechanic123",
  "actions": [
    "sovd:meta:read",
    "sovd:logs:read",
    "sovd:configuration:read",
    "sovd:data:read",
    "sovd:faults:read",
    "sovd:operations:read",
    "sovd:health-monitoring:read"
  ]
}
```

**Operator (can execute):**

```json
{
  "user_id": "user:operator456",
  "actions": [
    "sovd:meta:read",
    "sovd:logs:read",
    "sovd:data:read",
    "sovd:operations:read",
    "sovd:operations:exec"
  ]
}
```

Add token in SOVD Tester → Settings → Access Token

## Services

| Service        | Port | URL                   |
| -------------- | ---- | --------------------- |
| SOVD Tester    | 8085 | http://localhost:8085 |
| SOVD Gateway   | 8080 | http://localhost:8080 |
| Token Service  | 8086 | http://localhost:8086 |
| SOVD Server 1  | 7690 | http://localhost:7690 |
| SOVD Server 2  | 7691 | http://localhost:7691 |
| AC Control     | 8082 | http://localhost:8082 |
| Health Monitor | 8083 | http://localhost:8083 |
| Light Control  | 8084 | http://localhost:8084 |
| MCP Server     | 7693 | http://localhost:7693 |

### Internal Ports

| Service            | Port       | Purpose            |
| ------------------ | ---------- | ------------------ |
| Gateway (internal) | 7660       | Behind Envoy proxy |
| OPA                | 8182, 9191 | Policy engine      |


## Troubleshooting

**Connection Failed:**

```powershell
docker compose ps
docker compose logs sovd-gateway-envoy
```

**401 Unauthorized:** Get token from http://localhost:8086/docs

**403 Forbidden:** Token missing required action

```powershell
docker compose logs sovd-gateway-opa
```

Required actions:

- Logs: `sovd:logs:read` (GET), `sovd:logs:write` (POST)
- Config: `sovd:configuration:read` (GET), `sovd:configuration:write` (PUT)
- Data: `sovd:data:read` (GET), `sovd:data:write` (PUT)
- Operations: `sovd:operations:read` (GET), `sovd:operations:exec` (POST)
- Health: `sovd:health-monitoring:read`
- Gateway: `sovd:meta:read`

**Service issues:**

```powershell
docker compose logs <service-name>
docker compose restart <service-name>
docker compose down && docker compose up --build
```

## Development

### Add New Service

1. Create directory under `sovd-apps/`
2. Implement FastAPI app
3. Add to `docker-compose.yaml`
4. Auto-registers on startup

Example:

```python
from fastapi import FastAPI

app = FastAPI(title="My Service")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Logs

```bash
docker compose logs -f                      # All services
docker compose logs -f sovd-gateway-envoy   # Specific service
docker compose logs sovd-gateway | grep ERROR
```

## Documentation

### API & Integration

- [API Reference](docs/api/API.md) - curl examples for all apps
- [MCP Tools](docs/api/MCP.md) - MCP tool naming and reference
- [n8n AI Setup](docs/ai/README.md) - AI agent workflow configuration

### Services

- [SOVD Gateway](sovd-gateway/README.md) - API aggregator with discovery
- [SOVD Server](sovd-server/README.md) - Service registry
- [SOVD Tester](sovd-tester/README.md) - Web UI for testing
- [Token Service](sovd-token-service/README.md) - JWT token issuer
- [MCP Server](mcp-server/README.md) - Model Context Protocol server

### Security

- [Gateway Sidecar](sovd-gateway-sidecar/README.md) - Envoy + OPA (JWT/auth)
- [Sidecar Pi](sovd-gateway-sidecar-pi/README.md) - Pi deployment config

### Apps

- [AC Control](sovd-apps/ac-control/README.md) - Climate control
- [Health Monitoring](sovd-apps/health-monitoring/README.md) - System diagnostics
- [Light Control](sovd-apps/light-control/README.md) - UART lighting
- [Light Control KUKSA](sovd-apps/light-control-kuksa/README.md) - KUKSA/VSS lighting

### Testing

- [Tests](test/README.md) - pytest suite
