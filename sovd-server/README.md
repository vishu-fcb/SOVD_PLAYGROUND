# SOVD Server

Service registry for SOVD applications with dynamic service registration and discovery.

## Quick Start

**Local Docker:**

```bash
docker compose up -d sovd-server-1 sovd-server-2
```

**Access:**

- Server 1: http://localhost:7690/docs
- Server 2: http://localhost:7691/docs

## Endpoints

| Endpoint            | Description              |
| ------------------- | ------------------------ |
| `/register`         | Register SOVD app        |
| `/services`         | List registered services |
| `/refresh`          | Refresh service registry |
| `/health`           | Server health check      |
| `/app/{app_name}/*` | Proxied app endpoints    |

## Configuration

| Variable    | Default | Description                        |
| ----------- | ------- | ---------------------------------- |
| `SERVER_ID` | -       | Server identifier (e.g., server-1) |

## Usage

**Register app:**

```bash
curl -X POST http://localhost:7690/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-app",
    "url": "http://my-app:8080",
    "type": "app",
    "endpoints": [],
    "metadata": {}
  }'
```

**List services:**

```bash
curl http://localhost:7690/services
```

**Access app via server:**

```bash
curl http://localhost:7690/app/ac-control/logs
```

## Architecture

- **Service Registry**: In-memory registry for apps
- **Dynamic Router**: Creates routes for registered apps
- **OpenAPI Merge**: Combines app specs into server schema
- **Proxy**: Routes requests to registered apps

## Auto-Registration

Apps auto-register on startup via `infrastructure/registration.py`:

```python
await register_with_server(
    gateway_url="http://sovd-server:7690",
    app_url="http://my-app:8080",
    app=fastapi_app
)
```
