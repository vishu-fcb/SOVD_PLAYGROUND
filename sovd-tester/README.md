# SOVD Tester

Web-based diagnostic tester for the SOVD Gateway with dynamic API discovery and interactive testing capabilities.

## Getting Started

Start the SOVD ecosystem:

```bash
cd hpc/sovd
docker compose up --build
```

Open the UI at **http://localhost:8085**

### Connect to Gateway

1. Click settings icon (⚙️)
2. Set **Gateway URL** to `http://localhost:8080`
3. Click **Save & Connect**

The tester automatically discovers running SOVD apps.

## Authentication

### Public Endpoints (No Token Required)

- `/discover` - Service discovery
- `/openapi.json` - API specification
- `/docs` - API documentation
- `/health` - Health check
- `/status` - Service status

### Protected Endpoints (Token Required)

Get a JWT token from **http://localhost:8086/docs**

Example token request:

```json
{
  "user_id": "user:tech123",
  "actions": ["sovd:meta:read", "sovd:logs:read", "sovd:operations:exec"]
}
```

Add the token in SOVD Tester settings and reconnect.

## Code Structure

Modular architecture organized by functionality:

```
js/
├── sovd-tester.js         # Entry point
├── ui.js                  # Main UI orchestrator
├── state.js               # Application state
├── api.js                 # Gateway connection
├── operations.js          # Operation execution
├── search.js              # Search functionality
├── chat.js                # AI assistant
├── utils.js               # Utilities
│
├── panels/                # UI panels
│   ├── health.js          # Health check panel
│   ├── api-docs.js        # API documentation panel
│   └── workflows.js       # n8n workflows panel
│
└── renderers/             # Reusable components
    ├── app-panel.js       # App operations renderer
    ├── schema.js          # Schema utilities
    └── search-results.js  # Search results renderer
```

## Development

### Adding a New Panel

1. Create panel module in `panels/`:

```javascript
// panels/my-panel.js
import { state } from "../state.js";

export function renderMyPanel() {
  const mainPanel = document.getElementById("main-panel");
  mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">my_icon</span>
            My Panel Title
        </div>
        <div class="content">
            <!-- Panel content -->
        </div>
    `;
}
```

2. Import in `ui.js`:

```javascript
import { renderMyPanel } from "./panels/my-panel.js";
```

3. Add routing in `ui.js`:

```javascript
export function selectApp(appName) {
  if (appName === "my-panel") {
    renderMyPanel();
    return;
  }
}
```

4. Add to sidebar in `index.html`:

```html
<div class="app-item" data-app="my-panel">
  <span class="material-icons">my_icon</span>
  <span>My Panel</span>
</div>
```

### Adding a Workflow

Edit `panels/workflows.js`:

```javascript
export const flowConfigs = [
  {
    id: "my-flow",
    title: "My Flow",
    description: "What this flow does",
    webhookUrl: "http://localhost:5678/webhook/my-webhook",
    workflowDef: {
      nodes: [
        /* ... */
      ],
      connections: {
        /* ... */
      },
    },
  },
];
```
