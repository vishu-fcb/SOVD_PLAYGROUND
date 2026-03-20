# Light Control KUKSA

SOVD app for vehicle lights via KUKSA databroker with bidirectional sync.

## Setup

### Local

```bash
# Start KUKSA
docker run -p 55555:55555 ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure

# Configure settings.py
KUKSA_IP = "127.0.0.1"
KUKSA_PORT = 55555
ENABLE_REGISTRATION = False

# Start app
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker compose up light-control-kuksa kuksa-databroker
```

Uses service names:

```yaml
KUKSA_IP=kuksa-databroker
KUKSA_PORT=55555
```

## API

http://localhost:8000/docs

## Supported Lights

| ID             | VSS Path                                                 |
| -------------- | -------------------------------------------------------- |
| Dome           | Vehicle.Cabin.Light.IsDomeOn                             |
| Hazard         | Vehicle.Body.Lights.IsHazardOn                           |
| LeftIndicator  | Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling  |
| RightIndicator | Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling |
| LowBeam        | Vehicle.Body.Lights.Beam.Low.IsOn                        |
| HighBeam       | Vehicle.Body.Lights.Beam.High.IsOn                       |

## Testing

```bash
# KUKSA CLI
docker run -it --rm --net=host ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main

# Test sync
actuate Vehicle.Cabin.Light.IsDomeOn true
actuate Vehicle.Body.Lights.IsHazardOn false
get Vehicle.Cabin.Light.IsDomeOn
```

## Config

| Variable            | Default                         | Description       |
| ------------------- | ------------------------------- | ----------------- |
| KUKSA_IP            | 127.0.0.1                       | Databroker IP     |
| KUKSA_PORT          | 55555                           | Databroker port   |
| ENABLE_REGISTRATION | False                           | SOVD registration |
| SERVER_URL          | http://sovd-server:7690         | SOVD server       |
| APP_URL             | http://light-control-kuksa:8085 | This app          |

## Troubleshooting

**Connection failed:**

- Check KUKSA running: `netstat -an | findstr ":55555"`
- Verify IP/port config
- Use `--insecure` flag

**Updates not reflected:**

- Format: `{"data": {"state": boolean}}`
- Check subscription in logs

**Docker networking:**

- Use service names in compose
- Start with `--insecure` for dev
