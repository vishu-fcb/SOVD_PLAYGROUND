# SOVD Gateway Sidecar

Envoy proxy with OPA for JWT authentication and policy-based authorization.

## Deployment Context

**Docker Compose** - Local development environment

Configuration files used by `docker-compose.yaml` services:
- `envoy.yaml` - Envoy proxy config
- `policy.rego` - OPA authorization policy

## Components

- **Envoy Proxy** (Port 8080) - JWT validation, CORS, request forwarding
- **OPA Policy** (Port 8182, 9191) - Action-based authorization

## Flow

1. Client sends request with `Authorization: Bearer <token>`
2. Envoy validates JWT signature and expiration
3. Envoy forwards JWT payload to OPA via `x-jwt-payload` header
4. OPA evaluates policy and allows/denies request
5. If allowed, forwards to SOVD Gateway; else returns 403

## Public Endpoints

No authentication required:

- `/discover`
- `/openapi.json`
- `/docs`, `/redoc`
- `/health`, `/status`
- `/refresh-docs`

## Protected Endpoints

All `/app/*` endpoints require JWT with appropriate SOVD actions.

### SOVD Actions

| Action                        | Description        | Endpoints                             |
| ----------------------------- | ------------------ | ------------------------------------- |
| `sovd:meta:read`              | Gateway metadata   | `/servers`, `/endpoint-mapping`       |
| `sovd:logs:read`              | Read logs          | `GET /app/*/logs`                     |
| `sovd:logs:write`             | Write logs         | `POST /app/*/logs`                    |
| `sovd:configuration:read`     | Read config        | `GET /app/*/configuration`            |
| `sovd:configuration:write`    | Update config      | `PUT /app/*/configuration/*`          |
| `sovd:data:read`              | Read data          | `GET /app/*/data`                     |
| `sovd:data:write`             | Update data        | `PUT /app/*/data/*`                   |
| `sovd:faults:read`            | Read faults        | `GET /app/*/faults`                   |
| `sovd:faults:write`           | Clear faults       | `DELETE /app/*/faults/*`              |
| `sovd:operations:read`        | List operations    | `GET /app/*/operations`               |
| `sovd:operations:exec`        | Execute operations | `POST /app/*/operations/*/executions` |
| `sovd:health-monitoring:read` | System monitoring  | `GET /app/health-monitoring/*`        |

## JWT Format

```json
{
  "sub": "user@example.com",
  "authorization_details": [
    {
      "type": "sovd",
      "actions": ["sovd:logs:read", "sovd:data:read"]
    }
  ]
}
```

## Troubleshooting

**401 Unauthorized**

- Missing, expired, or invalid token signature
- Check `Authorization: Bearer <token>` header
- Verify ES256 algorithm and not expired

**403 Forbidden**

- Token missing required SOVD action
- Check OPA logs: `docker compose logs sovd-gateway-opa`
- Verify action for endpoint

**503 Service Unavailable**

- OPA not responding
- Check: `docker compose ps sovd-gateway-opa`

## Configuration

### Add Public Endpoint

Edit `policy.rego` → `public_endpoints` set

### Add Resource Type

Edit `policy.rego` → `authorization_rules`:

```rego
authorization_rules := {
    "new-resource": {
        "GET": "sovd:new-resource:read",
        "POST": "sovd:new-resource:write"
    }
}
```

### Update JWT Keys

Edit `envoy.yaml` → `local_jwks` with new public key

## Monitoring

```bash
# Envoy logs
docker compose logs -f sovd-gateway-envoy

# OPA decision logs
docker compose logs -f sovd-gateway-opa

# Envoy admin
curl http://localhost:9901/config_dump
```
