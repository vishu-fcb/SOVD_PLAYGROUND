# MCP Server

Model Context Protocol server that exposes SOVD Gateway APIs as MCP tools for AI agents.

## Quick Start

**Local Docker:**

```bash
docker compose up -d mcp-server
```

**Access:**

- MCP endpoint: http://localhost:7693/mcp

## Configuration

| Variable                                         | Default                    | Description                                  |
| ------------------------------------------------ | -------------------------- | -------------------------------------------- |
| `SOVD_GW_URL`                                    | `http://sovd-gateway:7660` | SOVD Gateway URL                             |
| `MCP_LOCAL_OPENAPI`                              | `true`                     | Use local openapi.json vs fetch from gateway |
| `FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER` | `true`                     | Enable experimental OpenAPI parser           |

## Usage

**n8n Integration:**

Configure n8n workflow to connect to MCP server:

```
MCP Server URL: http://mcp-server:7693/mcp
```

See `docs/ai/README.md` for full n8n configuration guide.

**Available Tools:**

All SOVD Gateway endpoints are exposed as MCP tools following the naming pattern:

```
{action}_{app_name}_{resource}
```

Example tools:

- `get_ac_control_logs` - Retrieve AC logs
- `execute_ac_control_operation` - Execute AC operation
- `get_light_control_data` - List light states
- `execute_light_control_operation` - Control lights

See `docs/api/MCP.md` for complete tool reference.

## Development

**Local Run:**

```bash
cd mcp-server
pip install -r requirements.txt
python main.py
```

**Update OpenAPI Spec:**

```bash
# Fetch latest spec from gateway
curl http://localhost:7660/openapi.json > openapi.json
```

## Architecture

- **FastMCP**: Generates MCP tools from OpenAPI spec
- **httpx**: HTTP client for SOVD Gateway communication
- **Dynamic Loading**: Tools auto-generated from OpenAPI schema
