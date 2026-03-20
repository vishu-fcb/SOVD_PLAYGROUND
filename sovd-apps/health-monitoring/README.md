# Health Monitoring

SOVD app for system diagnostics - CPU, memory, disk, network, and process monitoring.

## Quick Start

**Local Docker:**

```bash
docker compose up -d health-monitoring
```

**Access:**

- API: http://localhost:8083/docs

## Endpoints

| Endpoint             | Description             |
| -------------------- | ----------------------- |
| `/health/system`     | CPU, memory, disk usage |
| `/health/processes`  | Running processes       |
| `/health/network`    | Network interfaces      |
| `/health/filesystem` | Filesystem mounts       |

## Testing

**Via curl:**

```bash
# System health
curl http://localhost:8083/health/system

# Process list
curl http://localhost:8083/health/processes

# Network interfaces
curl http://localhost:8083/health/network

# Filesystem info
curl http://localhost:8083/health/filesystem
```

**Via MCP Server:**

```bash
# Available as MCP tools:
health_monitoring_get_system_health
health_monitoring_get_processes
health_monitoring_get_network
health_monitoring_get_filesystem
```

## Configuration

| Variable              | Default                         | Description               |
| --------------------- | ------------------------------- | ------------------------- |
| `APP_URL`             | `http://health-monitoring:8083` | Service URL               |
| `SERVER_URL`          | `http://sovd-server:7690`       | SOVD Server URL           |
| `ENABLE_REGISTRATION` | `true`                          | Auto-register with server |

## Note

Requires `pid: host` in docker-compose for full process visibility.
