# SOVD Gateway

API aggregator that discovers and merges SOVD servers into a unified gateway.

## Quick Start

**Local Docker:**

```bash
docker compose up -d sovd-gateway
```

**Access:**

- API: http://localhost:7660/docs
- Behind Envoy (with auth): http://localhost:8080/docs

## Endpoints

| Endpoint            | Description                     |
| ------------------- | ------------------------------- |
| `/discover`         | Discover and merge SOVD servers |
| `/servers`          | List registered SOVD servers    |
| `/health`           | Gateway health check            |
| `/app/{app_name}/*` | Proxied app endpoints           |

## Configuration

| Variable           | Default                                               | Description                 |
| ------------------ | ----------------------------------------------------- | --------------------------- |
| `SOVD_SERVER_URLS` | `http://sovd-server-1:7690,http://sovd-server-2:7691` | Comma-separated server URLs |

## Usage

**Discover servers:**

```bash
curl -X POST http://localhost:7660/discover
```

**List servers:**

```bash
curl http://localhost:7660/servers
```

**Access app via gateway:**

```bash
curl http://localhost:7660/app/ac-control/logs
```

## Architecture

- **Dynamic Router**: Creates routes for discovered apps
- **OpenAPI Merge**: Combines server specs into unified schema
- **Proxy**: Routes requests to appropriate SOVD servers
- **Registry**: Maintains server and app inventory

## Development

```bash
cd sovd-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 7660
```
