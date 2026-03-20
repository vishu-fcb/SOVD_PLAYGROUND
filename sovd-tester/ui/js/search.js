import { state } from './state.js';
import { renderSearchResults, selectApp } from './ui.js';

export function performSearch(searchTerm) {
    if (!searchTerm) {
        state.searchResults = [];
        if (state.currentApp) {
            selectApp(state.currentApp);
        }
        return;
    }

    const results = [];

    state.apps.forEach(app => {
        Object.values(app.operationGroups).forEach(operations => {
            operations.forEach(op => {
                const searchableText = `${op.method} ${op.path} ${op.summary} ${op.description}`.toLowerCase();
                if (searchableText.includes(searchTerm)) {
                    results.push({
                        app: app,
                        operation: op,
                        relevance: calculateRelevance(searchableText, searchTerm)
                    });
                }
            });
        });
    });

    results.sort((a, b) => b.relevance - a.relevance);
    
    state.searchResults = results;

    renderSearchResults(results, searchTerm);
}

export function calculateRelevance(text, term) {
    let score = 0;
    if (text.startsWith(term)) score += 10;
    if (text.includes(` ${term}`)) score += 5;
    const occurrences = (text.match(new RegExp(term, 'g')) || []).length;
    score += occurrences;
    return score;
}
