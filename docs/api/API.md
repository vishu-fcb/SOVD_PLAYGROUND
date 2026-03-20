# SOVD API Reference

Base URL: `http://localhost:7660/app/{app-name}`

## AC Control (`ac-control`)

### Logs

**List logs:**

```bash
curl http://localhost:7660/app/ac-control/logs
```

**Add log entry:**

```bash
curl -X POST http://localhost:7660/app/ac-control/logs \
  -H "Content-Type: application/json" \
  -d '{"event": "Manual AC adjustment"}'
```

### Configuration

**Get config:**

```bash
curl http://localhost:7660/app/ac-control/configuration
```

**Update config key:**

```bash
curl -X PUT http://localhost:7660/app/ac-control/configuration/max_items \
  -H "Content-Type: application/json" \
  -d '{"value": 20}'
```

Note: AC mode and fan speed are in data items, not configuration.

### Data Items

**List all data:**

```bash
curl http://localhost:7660/app/ac-control/data
```

Response includes:

- `AC` - Mode (highspeed/eco/off) and FanSpeed (0-5)
- `RoomTemp` - Current temperature

### Operations

**List operations:**

```bash
curl http://localhost:7660/app/ac-control/operations
```

Available operations:

- `set_highspeed` - Max cooling (fan: 5)
- `set_eco` - Energy efficient (fan: 2)
- `set_off` - AC off (fan: 0)

**Execute operation:**

```bash
curl -X POST http://localhost:7660/app/ac-control/operations/set_highspeed/executions \
  -H "Content-Type: application/json" \
  -d '{"parameters": {}}'
```

---

## Health Monitoring (`health-monitoring`)

### System Health

```bash
curl http://localhost:7660/app/health-monitoring/health
```

Returns CPU, memory, platform info.

### Processes

```bash
curl http://localhost:7660/app/health-monitoring/proc
```

### Filesystem

```bash
curl http://localhost:7660/app/health-monitoring/fs
```

---

## Light Control (`light-control-kuksa`)

### Configuration

**Get config:**

```bash
curl http://localhost:7660/app/light-control/configuration
```

**Update config key:**

```bash
curl -X PUT http://localhost:7660/app/light-control/configuration/brightness \
  -H "Content-Type: application/json" \
  -d '{"value": 100}'
```

### Data Items

**List all lights:**

```bash
curl http://localhost:7660/app/light-control/data
```

Available lights: Dome, BeamLow, BeamHigh, FogFront, FogRear, IndicatorLeft, IndicatorRight, Backup, Brake

**Update light state:**

```bash
curl -X PUT http://localhost:7660/app/light-control/data/Dome \
  -H "Content-Type: application/json" \
  -d '{"data": {"state": true}}'
```

### Operations

**List operations:**

```bash
curl http://localhost:7660/app/light-control/operations
```

Available operations:

- `toggle_beam` - Toggle low/high beam
- `toggle_fog` - Toggle fog lights
- `toggle_front` - Toggle front lights
- `toggle_rear` - Toggle rear lights
- `toggle_hazard` - Toggle hazard lights
- `set_all_on` - All lights ON
- `set_all_off` - All lights OFF

**Execute operation:**

```bash
curl -X POST http://localhost:7660/app/light-control/operations/set_all_off/executions \
  -H "Content-Type: application/json" \
  -d '{"parameters": {}}'
```
