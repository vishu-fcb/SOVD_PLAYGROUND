# n8n SOVD Tester Configuration

## Components

- **n8n** (port 5678) - Workflow automation with AI agent
- **MCP Server** (port 7693) - Exposes SOVD Gateway APIs as MCP tools
- **SOVD Gateway** (port 7660/8080) - Backend API aggregator
- **SOVD Tester UI** (port 8085) - Frontend interface

## Local Docker Setup

All services in same Docker network, use service names:

```yaml
# docker-compose.yaml
n8n:
  environment:
    - N8N_CORS_ORIGINS=http://localhost:8085,http://127.0.0.1:8085

mcp-server:
  environment:
    - SOVD_GW_URL=http://sovd-gateway:7660
```

**MCP Server URL in n8n:** `http://mcp-server:7693/mcp`

### MCP Server Config

**On VIC (recommended):**

**MCP URL in n8n:** `http://192.168.10.12:7693/mcp`