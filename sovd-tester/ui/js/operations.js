import { state } from './state.js';

export async function executeOperation(index, fromSearch = false) {
    let operation;
    let appName;
    
    if (fromSearch) {
        if (!state.searchResults || !state.searchResults[index]) {
            console.error('Search result not found at index:', index);
            return;
        }
        const result = state.searchResults[index];
        operation = result.operation;
        appName = result.app.name;
    } else {
        const app = state.apps.find(a => a.name === state.currentApp);
        if (!app) return;
        operation = app.operations[index];
        appName = app.name;
    }

    if (!operation) return;

    const resultDiv = document.getElementById(`result-${index}`);
    if (!resultDiv) {
        console.error('Result div not found:', `result-${index}`);
        return;
    }
    
    resultDiv.innerHTML = '<div class="spinner"></div>';

    // Build URL with path parameters
    let url = state.gatewayUrl + operation.path;
    const queryParams = [];

    // Collect parameters
    if (operation.parameters) {
        operation.parameters.forEach((param, pIdx) => {
            const inputId = `param-${index}-${pIdx}`;
            const value = document.getElementById(inputId)?.value;

            if (value) {
                if (param.in === 'path') {
                    url = url.replace(`{${param.name}}`, encodeURIComponent(value));
                } else if (param.in === 'query') {
                    queryParams.push(`${param.name}=${encodeURIComponent(value)}`);
                }
            }
        });
    }

    if (queryParams.length > 0) {
        url += '?' + queryParams.join('&');
    }

    // Build request body
    let body = null;
    if (operation.requestBody) {
        const bodyInput = document.getElementById(`body-${index}`)?.value;
        if (bodyInput) {
            try {
                body = JSON.stringify(JSON.parse(bodyInput));
            } catch (e) {
                resultDiv.innerHTML = `
                    <div class="result-container">
                        <div class="result-status">
                            <span class="action-method method-delete">ERROR</span>
                        </div>
                        <div class="result-body">
                            <div class="result-json">Invalid JSON in request body</div>
                        </div>
                    </div>
                `;
                return;
            }
        } else {
            // If operation requires a body but no input provided, send empty body
            body = JSON.stringify({});
        }
    }

    // Execute request
    const startTime = Date.now();
    try {
        const options = {
            method: operation.method,
            headers: {}
        };

        // Add JWT token if available
        if (state.accessToken) {
            options.headers['Authorization'] = `Bearer ${state.accessToken}`;
        }

        if (body) {
            options.body = body;
            options.headers['Content-Type'] = 'application/json';
        }

        const response = await fetch(url, options);
        const latency = Date.now() - startTime;

        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        // Generate status description
        const statusDescriptions = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            422: 'Validation Error',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout'
        };
        const statusDesc = statusDescriptions[response.status] || `HTTP ${response.status}`;

        resultDiv.innerHTML = `
            <div class="result-container">
                <div class="result-header">
                    <div class="result-status">
                        <span class="action-method method-${response.ok ? 'get' : 'delete'}">${response.status}</span>
                        <span class="result-status-text">${statusDesc}</span>
                    </div>
                    <span class="result-latency">${latency}ms</span>
                </div>
                <div class="result-body">
                    <pre class="result-json">${typeof data === 'object' ? JSON.stringify(data, null, 2) : data}</pre>
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
                    <pre class="result-json">${error.message}</pre>
                </div>
            </div>
        `;
    }
}
