# SOVD Gateway Sidecar (Pi)

Envoy proxy with OPA configuration for Raspberry Pi deployment in Trucky Ankaios cluster.

## Deployment Context

**Ankaios on VCM** - deployment via `configs/ankaios/common/sovd.yaml`

Configuration files for Ankaios manifest:
- `envoy.yaml` - Envoy proxy config (mounted at `/home/vcm/Documents/ankaios_deploy/sovd/`)
- `policy.rego` - OPA authorization policy (mounted at `/home/vcm/Documents/ankaios_deploy/sovd/`)

## Components

- **Envoy Proxy** (Port 8080) - JWT validation, CORS, routing
- **OPA** (Ports 8181, 9191) - Authorization policy engine

Runs on VCM Raspberry Pi with:
- ARM64 container image: `ghcr.io/mager-m/opa-envoy:sha-7076fc1`
- `--net=host` networking
- Dependencies: SOVD Gateway, SOVD Servers

## Differences from Docker Compose Version

- Deployed via Ankaios manifest (not docker-compose)
- Uses `--net=host` networking
- Config files mounted from `/home/vcm/Documents/ankaios_deploy/sovd/`
- Same authentication flow and SOVD actions
- Same public/protected endpoint configuration

## Configuration

### Ankaios Deployment

Defined in `configs/ankaios/common/sovd.yaml`:
- Runs on **VCM agent** (not VIC)
- SOVD Gateway connects to servers: `http://192.168.10.11:7690` (VCM), `http://192.168.10.12:7691` (VIC)

### Envoy Settings

- Admin port: 9901
- Listener port: 8080
- OPA gRPC: `0.0.0.0:9191`
- Upstream SOVD Gateway on VCM via `--net=host`

### Policy

Same as docker-compose version - see `sovd-gateway-sidecar/README.md` for:

- SOVD actions table
- JWT format
- Troubleshooting
- Configuration

## Network

VCM IP: `192.168.10.11` (where sidecar runs)
VIC IP: `192.168.10.12`

Access from CU or Infrastructure Pi:

```bash
curl -H "Authorization: Bearer <token>" \
  http://192.168.10.11:8080/app/ac-control/logs
```

## Monitoring

```bash
# Envoy admin (on Pi)
curl http://localhost:9901/config_dump

# Check upstream health
curl http://localhost:9901/clusters
```
