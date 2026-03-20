import { state } from '../state.js';
import { getAppIcon } from '../utils.js';
import { renderResponseInfo, generateSchemaTemplate, resolveSchemaRefs } from './schema.js';

export function renderSearchResults(results, searchTerm) {
    const mainPanel = document.getElementById('main-panel');
    
    if (results.length === 0) {
        mainPanel.innerHTML = `
            <div class="section-title">
                <span class="material-icons">search</span>
                Search Results
            </div>
            <div class="empty-state">
                <span class="material-icons">search_off</span>
                <h3>No Results Found</h3>
                <p>No operations match "${searchTerm}"</p>
            </div>
        `;
        return;
    }

    mainPanel.innerHTML = `
        <div class="section-title">
            <span class="material-icons">search</span>
            Search Results (${results.length})
        </div>
        <div class="search-info">Showing results for: <strong>${searchTerm}</strong></div>
        <div class="action-grid">
            ${results.map((op, index) => renderSearchResultCard(op, index)).join('')}
        </div>
    `;
}

function renderSearchResultCard(result, index) {
    const op = result.operation;
    const app = result.app;
    const methodClass = `method-${op.method.toLowerCase()}`;
    const paramsHtml = renderSearchParameters(op, index);
    const responseHtml = renderResponseInfo(op);
    
    return `
        <div class="action-card">
            <div class="app-badge">
                <span class="material-icons">${getAppIcon(app.name)}</span>
                <span>${app.name}</span>
            </div>
            <div class="action-header">
                <div class="action-header-left">
                    <span class="action-method ${methodClass}">${op.method}</span>
                    <div class="action-title">${op.summary || 'Operation'}</div>
                </div>
                <button class="btn btn-primary btn-small" onclick="executeOperation(${index}, true)">
                    <span class="material-icons">play_arrow</span>
                    Execute
                </button>
            </div>
            <div class="action-path">${op.path}</div>
            ${op.description ? `<div class="action-description">${op.description}</div>` : ''}
            ${paramsHtml}
            ${responseHtml}
            <div id="result-${index}"></div>
        </div>
    `;
}

function renderSearchParameters(operation, index) {
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
