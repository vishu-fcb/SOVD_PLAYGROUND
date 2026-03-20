import { state } from '../state.js';

export function renderApiDocsPanel() {
    const mainPanel = document.getElementById('main-panel');
    
    if (!state.connected) {
        mainPanel.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">cloud_off</span>
                <h3>Not Connected</h3>
                <p>Please connect to the gateway first to view API documentation</p>
            </div>
        `;
        return;
    }

    mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">description</span>
            API Documentation
        </div>
        <div class="action-grid">
            <div class="action-card">
                <div class="action-header">
                    <span class="material-icons" style="color: var(--md-sys-color-primary);">code</span>
                    <div class="action-title">Interactive API Documentation (Swagger UI)</div>
                </div>
                <div class="action-description">
                    Interactive documentation with built-in request testing and schema visualization
                </div>
                <button class="btn btn-primary btn-small" onclick="openApiDocs('/docs')">
                    <span class="material-icons">open_in_new</span>
                    Open Swagger UI
                </button>
                <button class="btn btn-secondary btn-small" style="margin-top: 8px;" onclick="embedApiDocs('/docs')">
                    <span class="material-icons">web</span>
                    Embed Here
                </button>
            </div>
            
            <div class="action-card">
                <div class="action-header">
                    <span class="material-icons" style="color: var(--md-sys-color-secondary);">menu_book</span>
                    <div class="action-title">API Reference (ReDoc)</div>
                </div>
                <div class="action-description">
                    Clean, searchable API reference documentation with detailed schemas
                </div>
                <button class="btn btn-primary btn-small" onclick="openApiDocs('/redoc')">
                    <span class="material-icons">open_in_new</span>
                    Open ReDoc
                </button>
                <button class="btn btn-secondary btn-small" style="margin-top: 8px;" onclick="embedApiDocs('/redoc')">
                    <span class="material-icons">web</span>
                    Embed Here
                </button>
            </div>

            <div class="action-card">
                <div class="action-header">
                    <span class="material-icons" style="color: var(--md-sys-color-tertiary);">data_object</span>
                    <div class="action-title">OpenAPI Specification (JSON)</div>
                </div>
                <div class="action-description">
                    Raw OpenAPI 3.0 specification in JSON format
                </div>
                <button class="btn btn-primary btn-small" onclick="openApiDocs('/openapi.json')">
                    <span class="material-icons">open_in_new</span>
                    Open JSON
                </button>
                <button class="btn btn-secondary btn-small" style="margin-top: 8px;" onclick="downloadOpenApiSpec()">
                    <span class="material-icons">download</span>
                    Download
                </button>
            </div>
        </div>
        <div id="api-docs-embed" style="margin-top: 20px;"></div>
    `;
}

function openApiDocs(path) {
    const url = `${state.gatewayUrl}${path}`;
    window.open(url, '_blank');
}

function embedApiDocs(path) {
    const embedContainer = document.getElementById('api-docs-embed');
    const url = `${state.gatewayUrl}${path}`;
    
    embedContainer.innerHTML = `
        <div class="embed-header">
            <div class="section-title">
                <span class="material-icons">web</span>
                Embedded API Documentation
            </div>
            <button class="btn btn-secondary btn-small" onclick="closeEmbeddedDocs()">
                <span class="material-icons">close</span>
                Close
            </button>
        </div>
        <iframe 
            src="${url}" 
            style="width: 100%; height: 600px; border: 1px solid var(--md-sys-color-outline); border-radius: 8px;"
            title="API Documentation">
        </iframe>
    `;
}

function closeEmbeddedDocs() {
    document.getElementById('api-docs-embed').innerHTML = '';
}

async function downloadOpenApiSpec() {
    try {
        const response = await fetch(`${state.gatewayUrl}/openapi.json`);
        const spec = await response.json();
        
        const blob = new Blob([JSON.stringify(spec, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sovd-gateway-openapi.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Failed to download OpenAPI spec: ' + error.message);
    }
}

window.openApiDocs = openApiDocs;
window.embedApiDocs = embedApiDocs;
window.closeEmbeddedDocs = closeEmbeddedDocs;
window.downloadOpenApiSpec = downloadOpenApiSpec;
