# Light Control

SOVD app for vehicle lighting control via UART/serial communication.

## Quick Start

**Local Docker:**

```bash
docker compose up -d light-control
```

**Access:**

- API: http://localhost:8084/docs

## Operations

| Operation       | Description            |
| --------------- | ---------------------- |
| `toggle_beam`   | Toggle low beam lights |
| `toggle_fog`    | Toggle fog lights      |
| `toggle_front`  | Toggle front lights    |
| `toggle_rear`   | Toggle rear lights     |
| `toggle_hazard` | Toggle hazard lights   |

## Testing

**Via curl:**

```bash
# Get current light state
curl http://localhost:8084/data

# Execute operation
curl -X POST http://localhost:8084/operations/toggle_beam/execute

# Check specific light
curl http://localhost:8084/data/Lights
```

**Via MCP Server:**

```bash
# Available as MCP tools:
light_control_toggle_beam
light_control_toggle_fog
light_control_toggle_front
light_control_toggle_rear
light_control_toggle_hazard
```

## Data Items

**Lights**: Beam, Fog, Front, Rear, Hazard status (currentData/lighting)

## Configuration

| Variable              | Default                     | Description               |
| --------------------- | --------------------------- | ------------------------- |
| `APP_URL`             | `http://light-control:8084` | Service URL               |
| `SERVER_URL`          | `http://sovd-server:7690`   | SOVD Server URL           |
| `ENABLE_REGISTRATION` | `true`                      | Auto-register with server |
| `SERIAL_PORT`         | `/dev/ttyUSB0`              | UART device path          |
| `BAUD_RATE`           | `115200`                    | Serial baud rate          |

## Hardware

Uses modular operation manager with UART communication to physical light controllers.
