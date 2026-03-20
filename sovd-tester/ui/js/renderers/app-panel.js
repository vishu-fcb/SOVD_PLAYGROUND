import { state } from '../state.js';
import { getAppIcon } from '../utils.js';
import { renderResponseInfo, renderSchemaInfo, generateSchemaTemplate, resolveSchemaRefs } from './schema.js';

export function renderAppPanel(app) {
    const mainPanel = document.getElementById('main-panel');
    
    // Flatten operations with global index
    app.operations = [];
    const groupsHtml = Object.entries(app.operationGroups).map(([groupName, operations]) => {
        const groupDisplayName = groupName.charAt(0).toUpperCase() + groupName.slice(1);
        const operationCards = operations.map(op => {
            const idx = app.operations.length;
            app.operations.push(op);
            return renderActionCard(op, idx);
        }).join('');
        
        return `
            <div class="operation-group">
                <div class="group-header">
                    <span class="material-icons">folder</span>
                    <h3>${groupDisplayName}</h3>
                </div>
                <div class="action-grid">
                    ${operationCards}
                </div>
            </div>
        `;
    }).join('');

    mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">${getAppIcon(app.name)}</span>
            ${app.displayName}
        </div>
        ${groupsHtml}
    `;
}

function renderActionCard(operation, index) {
    const methodClass = `method-${operation.method.toLowerCase()}`;
    const paramsHtml = renderParameters(operation, index);
    const responseHtml = renderResponseInfo(operation);

    return `
        <div class="action-card">
            <div class="action-header">
                <div class="action-header-left">
                    <span class="action-method ${methodClass}">${operation.method}</span>
                    <div class="action-title">${operation.summary || 'Operation'}</div>
                </div>
                <button class="btn btn-primary btn-small" onclick="executeOperation(${index})">
                    <span class="material-icons">play_arrow</span>
                    Execute
                </button>
            </div>
            <div class="action-path">${operation.path}</div>
            ${operation.description ? `<div class="action-description">${operation.description}</div>` : ''}
            ${paramsHtml}
            ${responseHtml}
            <div id="result-${index}"></div>
        </div>
    `;
}

function renderParameters(operation, index) {
    let html = '';

    if (operation.parameters && operation.parameters.length > 0) {
        operation.parameters.forEach((param, pIdx) => {
            const inputId = `param-${index}-${pIdx}`;
            const inputType = param.schema?.type === 'number' ? 'number' : 'text';
            const placeholder = param.example || param.schema?.example || param.description || param.name;
            html += `
                <div class="param-section">
                    <label class="param-label">${param.name} ${param.required ? '*' : ''} (${param.in})</label>
                    <input type="${inputType}" class="param-input" id="${inputId}" 
                                   placeholder="${placeholder}"
                                   ${param.required ? 'required' : ''}>
                </div>
            `;
        });
    }

    if (operation.requestBody) {
        const inputId = `body-${index}`;
        let schema = operation.requestBody?.content?.['application/json']?.schema;
        const example = operation.requestBody?.content?.['application/json']?.example;
        const examples = operation.requestBody?.content?.['application/json']?.examples;
        
        if (schema && state.openApiSpec) {
            schema = resolveSchemaRefs(schema, state.openApiSpec);
        }
        
        let template;
        if (example) {
            template = example;
        } else if (examples && Object.keys(examples).length > 0) {
            const firstExampleKey = Object.keys(examples)[0];
            template = examples[firstExampleKey].value || examples[firstExampleKey];
        } else if (schema) {
            template = generateSchemaTemplate(schema, state.openApiSpec);
        } else {
            template = {};
        }
        
        const templateJson = JSON.stringify(template, null, 2);

        html += `
            <div class="param-section">
                <label class="param-label">Request Body (JSON)
                    <button class="btn-icon" onclick="formatJson('${index}')" title="Format JSON">
                        <span class="material-icons">code</span>
                    </button>
                </label>
                <textarea class="param-input" id="${inputId}" rows="6">${templateJson}</textarea>
                <div class="param-hint">Template based on schema. Modify as needed.</div>
            </div>
        `;
    }

    return html;
}
