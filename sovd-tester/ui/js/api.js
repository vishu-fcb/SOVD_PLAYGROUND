import { state } from './state.js';
import { parseAppsFromSpec, renderApps, selectApp } from './ui.js';

export async function connectToGateway() {
    const url = document.getElementById('gateway-url').value.trim();
    if (!url) return;

    state.gatewayUrl = url;
    localStorage.setItem('sovd-gateway-url', url);

    const headers = {};
    if (state.accessToken) {
        headers['Authorization'] = `Bearer ${state.accessToken}`;
    }

    try {
        await fetch(`${url}/discover`, { 
            method: 'POST',
            headers: headers
        });

        try {
            await fetch(`${url}/refresh-docs`, { 
                method: 'POST',
                headers: headers
            });
        } catch (e) {
        }

        const response = await fetch(`${url}/openapi.json`, {
            headers: headers
        });
        
        if (!response.ok) {
            let errorMsg = 'Failed to fetch OpenAPI spec';
            if (response.status === 401) {
                errorMsg = 'Authentication failed: Invalid or expired access token';
            } else if (response.status === 403) {
                errorMsg = 'Access denied: Insufficient permissions to access OpenAPI spec';
            }
            throw new Error(errorMsg);
        }

        state.openApiSpec = await response.json();
        state.connected = true;

        updateConnectionStatus(true);
        parseAppsFromSpec();
        renderApps();
        updateMainPanel();
        document.getElementById('refresh-btn').style.display = 'inline-flex';
        document.getElementById('header-search').style.display = 'block';
        document.getElementById('settings-dropdown').classList.remove('show');

    } catch (error) {
        console.error('Connection error:', error);
        alert('Failed to connect to gateway: ' + error.message);
        updateConnectionStatus(false);
        updateMainPanel();
        throw error;
    }
}

export async function refreshDocs() {
    const refreshBtn = document.getElementById('refresh-btn');
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<span class="spinner"></span> Refreshing...';

    const headers = {};
    if (state.accessToken) {
        headers['Authorization'] = `Bearer ${state.accessToken}`;
    }

    try {
        await fetch(`${state.gatewayUrl}/refresh-docs`, { 
            method: 'POST',
            headers: headers
        });
        const response = await fetch(`${state.gatewayUrl}/openapi.json`, {
            headers: headers
        });
        state.openApiSpec = await response.json();
        parseAppsFromSpec();
        renderApps();
        if (state.currentApp) {
            selectApp(state.currentApp);
        }
    } catch (error) {
        console.error('Refresh error:', error);
        alert('Failed to refresh: ' + error.message);
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<span class="material-icons">refresh</span> Refresh';
    }
}

export function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');

    if (connected) {
        statusBadge.className = 'status-badge status-connected';
        statusBadge.innerHTML = '<span class="status-dot"></span><span>Connected</span>';
    } else {
        statusBadge.className = 'status-badge status-disconnected';
        statusBadge.innerHTML = '<span class="status-dot"></span><span>Disconnected</span>';
    }
}

export function updateMainPanel() {
    const mainPanel = document.getElementById('main-panel');
    
    if (state.connected) {
        // Show a welcome message when connected but no app is selected
        mainPanel.innerHTML = `
            <div class="welcome-state">
                <span class="material-icons" style="font-size: 64px; color: var(--md-sys-color-primary); margin-bottom: 16px;">check_circle</span>
                <h2>Connected to SOVD Gateway</h2>
                <p>Gateway connection established successfully. Select an application from the sidebar to get started.</p>
                <div class="quick-actions" style="margin-top: 24px;">
                    <button class="btn btn-primary" onclick="document.querySelector('[data-app=&quot;health&quot;]').click()">
                        <span class="material-icons">health_and_safety</span>
                        Check Health
                    </button>
                    <button class="btn btn-secondary" onclick="document.querySelector('[data-app=&quot;api-docs&quot;]').click()">
                        <span class="material-icons">description</span>
                        View API Docs
                    </button>
                </div>
            </div>
        `;
    } else {
        // Show the not connected state
        mainPanel.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">cloud_off</span>
                <h3>Not Connected</h3>
                <p>Click the Gateway button in the header to connect</p>
            </div>
        `;
    }
}
