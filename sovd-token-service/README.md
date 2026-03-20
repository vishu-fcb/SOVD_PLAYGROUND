# SOVD Token Service

JWT token issuer with ES256 signing and action-based authorization.

## Quick Start

**Generate keys:**

```bash
./utils/generate-key.sh
```

**Start service:**

```bash
python sovd-token-service.py
```

**Access:**

- UI: http://localhost:8000
- API: http://localhost:8000/docs
- JWKS: http://localhost:8000/.well-known/jwks.json

## SOVD Actions

Format: `sovd:resource:operation`

- `sovd:meta:read` - Metadata
- `sovd:logs:read`, `sovd:logs:write` - Logs
- `sovd:configuration:read`, `sovd:configuration:write` - Config
- `sovd:data:read`, `sovd:data:write` - Data
- `sovd:faults:read`, `sovd:faults:write` - Faults
- `sovd:operations:read`, `sovd:operations:exec` - Operations
- `sovd:health-monitoring:read` - Health

## Web UI Presets

1. **OEM Developer** - Full access (2h)
2. **Workshop Technician** - Diagnostics (1h)
3. **Vehicle Monitoring** - Read-only (1h)
4. **Read Only** - Metadata only (30m)
5. **Custom** - Manual config

## API Usage

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user:tech123",
    "actions": ["sovd:meta:read", "sovd:logs:read"],
    "expires_in": 3600
  }'
```

## JWT Format

```json
{
  "iss": "https://auth.oem.example.com",
  "sub": "user:tech123",
  "aud": "sovd-api",
  "authorization_details": [
    {
      "type": "sovd",
      "actions": ["sovd:logs:read", "sovd:data:read"]
    }
  ]
}
```

## Setup

### Generate Keys

```bash
./utils/generate-key.sh
```

Or manually:

```bash
mkdir -p keys
openssl ecparam -genkey -name prime256v1 -noout -out keys/private_key.pem
openssl ec -in keys/private_key.pem -pubout -out keys/public_key.pem
chmod 600 keys/private_key.pem
```

### Docker

```bash
# Generate keys first
./utils/generate-key.sh

# From hpc/sovd
docker compose up sovd-token-service

# Or standalone
docker build -t sovd-token-service .
docker run -d -p 8086:8000 \
  -v $(pwd)/keys:/app/keys:ro \
  sovd-token-service
```

## Configuration

Environment: `KEY_FILE` (default: keys/private_key.pem)

Defaults in `TokenRequest`:

```python
vin: str = "WVWZZZ1JZXW000000"
user_id: str = "user:tech123"
issuer: str = "https://auth.oem.example.com"
audience: str = "sovd-api"
expires_in: int = 3600
```
