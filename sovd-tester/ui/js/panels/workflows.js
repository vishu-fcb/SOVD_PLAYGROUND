import { state } from '../state.js';

// Static flow configurations with embedded n8n workflows
export const flowConfigs = [
    {
        id: 'sovd-diagnostic-flow',
        title: 'SOVD Diagnostic Flow',
        description: 'Execute diagnostic operations on vehicle systems',
        webhookUrl: 'http://localhost:5678/webhook/sovd-diagnostic',
        workflowDef: {
            nodes: [
                {
                    name: "Webhook",
                    type: "n8n-nodes-base.webhook",
                    position: [240, 300],
                    parameters: {
                        path: "sovd-diagnostic",
                        httpMethod: "POST"
                    },
                    typeVersion: 1
                },
                {
                    name: "Get Diagnostics",
                    type: "n8n-nodes-base.httpRequest",
                    position: [460, 300],
                    parameters: {
                        url: "http://gateway:7660/app/diagnostics/dtcs",
                        method: "GET"
                    },
                    typeVersion: 1
                },
                {
                    name: "Respond",
                    type: "n8n-nodes-base.respondToWebhook",
                    position: [680, 300],
                    parameters: {},
                    typeVersion: 1
                }
            ],
            connections: {
                "Webhook": {
                    main: [[{ node: "Get Diagnostics", type: "main", index: 0 }]]
                },
                "Get Diagnostics": {
                    main: [[{ node: "Respond", type: "main", index: 0 }]]
                }
            }
        }
    },
    {
        id: 'sovd-control-flow',
        title: 'SOVD Vehicle Control Flow',
        description: 'Execute control commands for vehicle actuators',
        webhookUrl: 'http://localhost:5678/webhook/sovd-control',
        workflowDef: {
            nodes: [
                {
                    name: "Webhook",
                    type: "n8n-nodes-base.webhook",
                    position: [240, 300],
                    parameters: {
                        path: "sovd-control",
                        httpMethod: "POST"
                    },
                    typeVersion: 1
                },
                {
                    name: "Execute Control",
                    type: "n8n-nodes-base.httpRequest",
                    position: [460, 300],
                    parameters: {
                        url: "http://gateway:7660/app/control/actuator",
                        method: "POST"
                    },
                    typeVersion: 1
                },
                {
                    name: "Respond",
                    type: "n8n-nodes-base.respondToWebhook",
                    position: [680, 300],
                    parameters: {},
                    typeVersion: 1
                }
            ],
            connections: {
                "Webhook": {
                    main: [[{ node: "Execute Control", type: "main", index: 0 }]]
                },
                "Execute Control": {
                    main: [[{ node: "Respond", type: "main", index: 0 }]]
                }
            }
        }
    }
];

export function renderN8nWorkflowPanel() {
    const mainPanel = document.getElementById('main-panel');
    
    const flowsHtml = flowConfigs.map((flow, index) => `
        <div class="flow-card">
            <div class="flow-header">
                <div class="flow-title-section">
                    <span class="material-icons">account_tree</span>
                    <div>
                        <h3 class="flow-title">${flow.title}</h3>
                        <p class="flow-description">${flow.description}</p>
                    </div>
                </div>
                <div class="flow-actions">
                    <button class="btn btn-primary" onclick="executeWorkflow('${flow.id}')">
                        <span class="material-icons">play_arrow</span>
                        Execute
                    </button>
                </div>
            </div>
            
            <div class="collapsible-section">
                <div class="collapsible-header" onclick="toggleCollapsible(this)">
                    <span class="material-icons collapsible-icon">chevron_right</span>
                    <span>Settings</span>
                </div>
                <div class="collapsible-content collapsed">
                    <div class="workflow-config">
                        <div class="input-field">
                            <label>Webhook URL</label>
                            <input type="text" id="webhook-url-${flow.id}" value="${flow.webhookUrl}">
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="workflow-viewer">
                <n8n-demo
                    clicktointeract="false"
                    workflow='${JSON.stringify(flow.workflowDef)}'
                ></n8n-demo>
            </div>
            
            <div id="workflow-response-${flow.id}" class="workflow-response"></div>
        </div>
    `).join('');
    
    mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">account_tree</span>
            SOVD Workflows
        </div>
        <div class="flows-container">
            ${flowsHtml}
        </div>
    `;
}

async function executeWorkflow(flowId) {
    const flow = flowConfigs.find(f => f.id === flowId);
    if (!flow) return;
    
    const webhookUrl = document.getElementById(`webhook-url-${flowId}`).value;
    const responseDiv = document.getElementById(`workflow-response-${flowId}`);
    
    responseDiv.innerHTML = `
        <div class="response-container">
            <div class="response-header">
                <span class="material-icons spinning">sync</span>
                <span>Executing workflow...</span>
            </div>
        </div>
    `;
    
    const startTime = Date.now();
    
    try {
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                timestamp: new Date().toISOString(),
                source: 'sovd-tester'
            })
        });
        
        const latency = Date.now() - startTime;
        const data = await response.json();
        
        const statusDescriptions = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable'
        };
        
        const statusDesc = statusDescriptions[response.status] || `HTTP ${response.status}`;
        
        responseDiv.innerHTML = `
            <div class="workflow-response-container">
                <div class="response-header-section">
                    <span class="material-icons">check_circle</span>
                    <span class="response-title">Workflow Response</span>
                </div>
                <div class="result-container">
                    <div class="result-header">
                        <div class="result-status">
                            <span class="action-method method-${response.ok ? 'get' : 'delete'}">${response.status}</span>
                            <span class="result-status-text">${statusDesc}</span>
                        </div>
                        <span class="result-latency">${latency}ms</span>
                    </div>
                    <div class="result-body">
                        <pre class="result-json">${JSON.stringify(data, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;
        
    } catch (error) {
        const latency = Date.now() - startTime;
        responseDiv.innerHTML = `
            <div class="workflow-response-container">
                <div class="response-header-section error">
                    <span class="material-icons">error</span>
                    <span class="response-title">Execution Failed</span>
                </div>
                <div class="result-container">
                    <div class="result-header">
                        <div class="result-status">
                            <span class="action-method method-delete">ERROR</span>
                            <span class="result-status-text">${error.message}</span>
                        </div>
                        <span class="result-latency">${latency}ms</span>
                    </div>
                    <div class="result-body">
                        <pre class="result-json">Check if the n8n workflow is active and the webhook URL is correct.</pre>
                    </div>
                </div>
            </div>
        `;
    }
}

window.executeWorkflow = executeWorkflow;
