import { state } from './state.js';
import { updateMainPanel } from './api.js';
import { getAppIcon } from './utils.js';
import { renderHealthPanel } from './panels/health.js';
import { renderApiDocsPanel } from './panels/api-docs.js';
import { renderN8nWorkflowPanel } from './panels/workflows.js';
import { renderAppPanel } from './renderers/app-panel.js';
import { renderSearchResults } from './renderers/search-results.js';

export function parseAppsFromSpec() {
    if (!state.openApiSpec || !state.openApiSpec.paths) {
        state.apps = [];
        return;
    }

    const appSet = new Set();
    const appData = {};

    for (const [path, methods] of Object.entries(state.openApiSpec.paths)) {
        const appMatch = path.match(/^\/app\/([^\/]+)/);
        if (appMatch) {
            const appName = appMatch[1].replace(/[{}]/g, '');
            if (!appName.includes('{')) {
                appSet.add(appName);
                if (!appData[appName]) {
                    appData[appName] = {};
                }

                for (const [method, operation] of Object.entries(methods)) {
                    if (typeof operation === 'object' && operation.summary) {
                        const pathAfterApp = path.replace(`/app/${appName}`, '');
                        const pathParts = pathAfterApp.split('/').filter(p => p && !p.startsWith('{'));
                        const pathGroup = pathParts.length > 0 ? pathParts[0] : 'general';
                        
                        if (!appData[appName][pathGroup]) {
                            appData[appName][pathGroup] = [];
                        }
                        
                        appData[appName][pathGroup].push({
                            method: method.toUpperCase(),
                            path: path,
                            summary: operation.summary,
                            description: operation.description,
                            parameters: operation.parameters || [],
                            requestBody: operation.requestBody,
                            responses: operation.responses,
                            operationId: operation.operationId
                        });
                    }
                }
            }
        }
    }

    state.apps = Array.from(appSet).map(name => ({
        name: name,
        displayName: name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        operationGroups: appData[name] || {}
    }));
}

export function renderApps() {
    const appsList = document.getElementById('apps-list');

    if (state.apps.length === 0) {
        appsList.innerHTML = '<div style="padding: 12px 24px; color: var(--md-sys-color-on-surface-variant); font-size: 14px;">No apps discovered</div>';
        return;
    }

    appsList.innerHTML = state.apps.map(app => `
        <div class="app-item" data-app="${app.name}">
            <span class="material-icons">${getAppIcon(app.name)}</span>
            <span>${app.displayName}</span>
        </div>
    `).join('');
}

export function selectApp(appName) {
    state.currentApp = appName;

    document.querySelectorAll('.app-item').forEach(item => {
        item.classList.toggle('active', item.dataset.app === appName);
    });

    if (appName === 'health') {
        renderHealthPanel();
    } else if (appName === 'api-docs') {
        renderApiDocsPanel();
    } else if (appName === 'n8n-workflow') {
        renderN8nWorkflowPanel();
    } else {
        const app = state.apps.find(a => a.name === appName);
        if (app) {
            renderAppPanel(app);
        }
    }
}

// Collapsible toggle function
window.toggleCollapsible = function(element) {
    const content = element.nextElementSibling;
    const icon = element.querySelector('.collapsible-icon');
    content.classList.toggle('collapsed');
    icon.textContent = content.classList.contains('collapsed') ? 'chevron_right' : 'expand_more';
};

// Export search results renderer
export { renderSearchResults };
