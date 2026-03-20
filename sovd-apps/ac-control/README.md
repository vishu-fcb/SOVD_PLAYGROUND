# AC Control

SOVD app for vehicle climate control with real-time temperature simulation.

## Quick Start

**Local Docker:**

```bash
docker compose up -d ac-control
```

**Access:**

- API: http://localhost:8082/docs
- Dashboard: http://localhost:8082/ac-dashboard

## Operations

| Operation       | Description                      |
| --------------- | -------------------------------- |
| `set_highspeed` | High-speed cooling (fan speed 5) |
| `set_eco`       | Eco mode cooling (fan speed 2)   |
| `set_off`       | Turn AC off                      |

## Testing

**Via curl:**

```bash
# Get current AC state
curl http://localhost:8082/data

# Execute operation
curl -X POST http://localhost:8082/operations/set_eco/execute

# Check room temperature
curl http://localhost:8082/data/RoomTemp
```

**Via MCP Server:**

```bash
# Available as MCP tools:
ac_control_set_highspeed
ac_control_set_eco
ac_control_set_off
```

## Data Items

- **AC**: Mode, FanSpeed (currentData/climate)
- **RoomTemp**: Temperature in °C (currentData/climate)

## Configuration

| Variable              | Default                   | Description               |
| --------------------- | ------------------------- | ------------------------- |
| `APP_URL`             | `http://ac-control:8082`  | Service URL               |
| `SERVER_URL`          | `http://sovd-server:7690` | SOVD Server URL           |
| `ENABLE_REGISTRATION` | `true`                    | Auto-register with server |

## Background Worker

Simulates temperature changes every 2 seconds:

- **Highspeed**: -0.5°C per cycle + drift
- **Eco**: -0.2°C per cycle + drift
- **Off**: Drifts back to ambient (28°C)
