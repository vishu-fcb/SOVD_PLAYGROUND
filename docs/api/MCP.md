# MCP Tool Reference

## Naming Pattern

`{action}_{app_name}_{resource}`

**Actions:**

- `get` - Retrieve data
- `add` - Add single item
- `update` - Modify data
- `delete` - Remove data
- `execute` - Run operation

**Apps:**

- `ac_control` - AC system
- `light_control` - Vehicle lights
- `health_monitoring` - System health

**Resources:**

- `logs` / `log` - Log entries
- `configuration` - Settings
- `data` / `data_item` - Data items
- `faults` / `fault` - Fault codes
- `operations` / `operation` - Operations

---

## AC Control Tools

| Tool                              | Endpoint                              | Purpose         |
| --------------------------------- | ------------------------------------- | --------------- |
| `get_ac_control_logs`             | GET `/logs`                           | List logs       |
| `add_ac_control_log`              | POST `/logs`                          | Add log entry   |
| `get_ac_control_configuration`    | GET `/configuration`                  | Get config      |
| `update_ac_control_configuration` | PUT `/configuration/{key}`            | Update config   |
| `get_ac_control_data`             | GET `/data`                           | List data items |
| `update_ac_control_data_item`     | PUT `/data/{item_id}`                 | Update data     |
| `get_ac_control_faults`           | GET `/faults`                         | List faults     |
| `delete_ac_control_fault`         | DELETE `/faults/{code}`               | Clear fault     |
| `get_ac_control_operations`       | GET `/operations`                     | List operations |
| `execute_ac_control_operation`    | POST `/operations/{op_id}/executions` | Execute op      |

**Operations:** `set_highspeed`, `set_eco`, `set_off`

---

## Light Control Tools

| Tool                                 | Endpoint                              | Purpose         |
| ------------------------------------ | ------------------------------------- | --------------- |
| `get_light_control_logs`             | GET `/logs`                           | List logs       |
| `add_light_control_log`              | POST `/logs`                          | Add log         |
| `get_light_control_configuration`    | GET `/configuration`                  | Get config      |
| `update_light_control_configuration` | PUT `/configuration/{key}`            | Update config   |
| `get_light_control_data`             | GET `/data`                           | List lights     |
| `update_light_control_data_item`     | PUT `/data/{item_id}`                 | Update light    |
| `get_light_control_operations`       | GET `/operations`                     | List operations |
| `execute_light_control_operation`    | POST `/operations/{op_id}/executions` | Execute op      |

**Operations:** `toggle_beam`, `toggle_fog`, `toggle_front`, `toggle_rear`, `toggle_hazard`, `set_all_on`, `set_all_off`

---

## Health Monitoring Tools

| Tool                           | Endpoint      | Purpose         |
| ------------------------------ | ------------- | --------------- |
| `get_health_monitoring_health` | GET `/health` | System health   |
| `get_health_monitoring_proc`   | GET `/proc`   | Processes       |
| `get_health_monitoring_fs`     | GET `/fs`     | Filesystem info |
| `get_health_monitoring_net`    | GET `/net`    | Network stats   |

---

## Usage Examples

### Execute Operation

```python
# 1. List operations
get_ac_control_operations()

# 2. Execute operation
execute_ac_control_operation(
    operation_id="set_highspeed",
    body={"parameters": {}}
)
```

### Update Data Item

```python
# 1. List items
get_light_control_data()

# 2. Update item
update_light_control_data_item(
    item_id="Dome",
    body={"data": {"state": true}}
)
```

### Common Patterns

- **Logs:** `get_{app}_logs`, `add_{app}_log`
- **Config:** `get_{app}_configuration`, `update_{app}_configuration`
- **Faults:** `get_{app}_faults`, `delete_{app}_fault`

**Note:** Always include request body for POST/PUT, even if empty: `{"parameters": {}}`
