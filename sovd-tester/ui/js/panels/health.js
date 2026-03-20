import { state } from '../state.js';

export function renderHealthPanel() {
    const mainPanel = document.getElementById('main-panel');
    mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">health_and_safety</span>
            Gateway Health
        </div>
        <div class="action-grid">
            <div class="action-card">
                <div class="action-header">
                    <span class="action-method method-get">GET</span>
                    <div class="action-title">Health Check</div>
                </div>
                <div class="action-path">/health</div>
                <div class="action-description">Check gateway health status</div>
                <button class="btn btn-primary btn-small" onclick="executeHealth()">
                    <span class="material-icons">play_arrow</span>
                    Execute
                </button>
                <div class="response-section">
                    <div class="response-info">
                        <strong>Response:</strong> 200 OK - Returns gateway health status
                    </div>
                </div>
                <div id="health-result"></div>
            </div>
        </div>
    `;
}

async function executeHealth() {
    const resultDiv = document.getElementById('health-result');
    resultDiv.innerHTML = '<div class="spinner"></div>';

    const startTime = Date.now();
    try {
        const response = await fetch(`${state.gatewayUrl}/health`);
        const latency = Date.now() - startTime;
        const data = await response.json();

        resultDiv.innerHTML = `
            <div class="result-container">
                <div class="result-header">
                    <div class="result-status">
                        <span class="action-method method-${response.ok ? 'get' : 'delete'}">${response.status}</span>
                        <span class="result-latency">${latency}ms</span>
                    </div>
                </div>
                <div class="result-body">
                    <div class="result-json">${JSON.stringify(data, null, 2)}</div>
                </div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-container">
                <div class="result-status">
                    <span class="action-method method-delete">ERROR</span>
                </div>
                <div class="result-body">
                    <div class="result-json">${error.message}</div>
                </div>
            </div>
        `;
    }
}

window.executeHealth = executeHealth;
