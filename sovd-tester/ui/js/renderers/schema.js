import { state } from '../state.js';

// Custom JSON stringifier that preserves object key order
function stringifyPreservingOrder(obj, indent = 2) {
    const spaces = ' '.repeat(indent);
    
    function stringify(value, depth = 0) {
        const currentIndent = ' '.repeat(depth * indent);
        const nextIndent = ' '.repeat((depth + 1) * indent);
        
        if (value === null) return 'null';
        if (value === undefined) return 'null';
        if (typeof value === 'string') return JSON.stringify(value);
        if (typeof value === 'number') return String(value);
        if (typeof value === 'boolean') return String(value);
        
        if (Array.isArray(value)) {
            if (value.length === 0) return '[]';
            const items = value.map(item => nextIndent + stringify(item, depth + 1)).join(',\n');
            return '[\n' + items + '\n' + currentIndent + ']';
        }
        
        if (typeof value === 'object') {
            const keys = Object.keys(value);
            if (keys.length === 0) return '{}';
            const items = keys.map(key => 
                nextIndent + JSON.stringify(key) + ': ' + stringify(value[key], depth + 1)
            ).join(',\n');
            return '{\n' + items + '\n' + currentIndent + '}';
        }
        
        return String(value);
    }
    
    return stringify(obj);
}

// Helper function to reorder example object to match schema properties order
function reorderExample(example, schema, openApiSpec) {
    // Handle arrays
    if (Array.isArray(example)) {
        if (!schema || !schema.items) {
            return example;
        }
        // Resolve $ref if present in items
        let itemSchema = schema.items;
        if (itemSchema.$ref && openApiSpec) {
            itemSchema = resolveSchemaRefs(itemSchema, openApiSpec);
        }
        // Recursively reorder each item in the array
        return example.map(item => reorderExample(item, itemSchema, openApiSpec));
    }
    
    // Only reorder if it's an object
    if (!example || typeof example !== 'object') {
        return example;
    }
    
    // Handle objects with properties (regular objects with defined fields)
    if (schema && schema.properties) {
        // Create new object with keys in the order defined by schema.properties
        const reordered = {};
        for (const key of Object.keys(schema.properties)) {
            if (key in example) {
                // Recursively reorder nested objects and arrays
                const value = example[key];
                const propSchema = schema.properties[key];
                if (value && typeof value === 'object' && propSchema) {
                    reordered[key] = reorderExample(value, propSchema, openApiSpec);
                } else {
                    reordered[key] = value;
                }
            }
        }
        
        // Add any keys from example that aren't in schema (shouldn't happen but be safe)
        for (const key of Object.keys(example)) {
            if (!(key in reordered)) {
                reordered[key] = example[key];
            }
        }
        
        return reordered;
    }
    
    // Handle Dict/Map types with additionalProperties (e.g., Dict[str, SomeModel])
    if (schema && schema.additionalProperties) {
        let valueSchema = schema.additionalProperties;
        if (valueSchema.$ref && openApiSpec) {
            valueSchema = resolveSchemaRefs(valueSchema, openApiSpec);
        }
        
        // Reorder each value in the dict according to its schema
        const reordered = {};
        for (const key of Object.keys(example)) {
            const value = example[key];
            if (value && typeof value === 'object') {
                reordered[key] = reorderExample(value, valueSchema, openApiSpec);
            } else {
                reordered[key] = value;
            }
        }
        return reordered;
    }
    
    // No schema to guide reordering, return as-is
    return example;
}

export function generateSchemaTemplate(schema, openApiSpec) {
    if (!schema || typeof schema !== 'object') {
        return null;
    }

    // Check for example (singular) - OpenAPI 3.0 standard
    if (schema.example !== undefined) {
        return reorderExample(schema.example, schema, openApiSpec);
    }

    // Check for examples (plural) array - some frameworks use this
    if (schema.examples && Array.isArray(schema.examples) && schema.examples.length > 0) {
        return reorderExample(schema.examples[0], schema, openApiSpec);
    }

    if (schema.type === 'object' && schema.properties) {
        const template = {};
        for (const [key, prop] of Object.entries(schema.properties)) {
            template[key] = generateSchemaTemplate(prop, openApiSpec);
        }
        return template;
    }

    if (schema.type === 'array' && schema.items) {
        const itemExample = generateSchemaTemplate(schema.items, openApiSpec);
        // If items have an example, return array with one item
        return itemExample !== null ? [itemExample] : [];
    }

    // Generate default values based on type when no example is provided
    if (schema.type) {
        switch (schema.type) {
            case 'string':
                return schema.format === 'date-time' ? '2025-01-01T00:00:00Z' : 'string';
            case 'integer':
                return 0;
            case 'number':
                return 0.0;
            case 'boolean':
                return false;
            case 'array':
                return [];
            case 'object':
                return {};
        }
    }

    return null;
}

export function resolveSchemaRefs(schema, openApiSpec) {
    if (!schema || !openApiSpec) {
        return schema;
    }

    if (schema.$ref) {
        const refPath = schema.$ref.replace('#/', '').split('/');
        let resolved = openApiSpec;
        for (const part of refPath) {
            resolved = resolved?.[part];
        }
        
        if (resolved && resolved.allOf) {
            const mergedSchema = {};
            resolved.allOf.forEach(item => {
                const resolvedItem = resolveSchemaRefs(item, openApiSpec);
                Object.keys(resolvedItem).forEach(key => {
                    mergedSchema[key] = resolvedItem[key];
                });
            });
            Object.keys(schema).forEach(key => {
                if (key !== '$ref') {
                    mergedSchema[key] = schema[key];
                }
            });
            return resolveSchemaRefs(mergedSchema, openApiSpec);
        }
        
        return resolveSchemaRefs(resolved, openApiSpec);
    }
    
    if (typeof schema === 'object' && !Array.isArray(schema)) {
        const resolvedSchema = {};
        for (const [key, value] of Object.entries(schema)) {
            resolvedSchema[key] = resolveSchemaRefs(value, openApiSpec);
        }
        return resolvedSchema;
    }
    
    if (Array.isArray(schema)) {
        return schema.map(item => resolveSchemaRefs(item, openApiSpec));
    }
    
    return schema;
}

export function renderSchemaInfo(operation) {
    if (!operation.requestBody?.content?.['application/json']?.schema) {
        return '';
    }
    
    let schema = operation.requestBody.content['application/json'].schema;
    
    if (state.openApiSpec) {
        schema = resolveSchemaRefs(schema, state.openApiSpec);
    }
    
    const schemaJson = JSON.stringify(schema, null, 2);
    
    return `
        <div class="schema-info">
            <div class="schema-title">Request Body Schema</div>
            <pre class="schema-display">${schemaJson}</pre>
        </div>
    `;
}

export function renderResponseInfo(operation) {
    if (!operation.responses) return '';
    
    // Standard status descriptions - matching operations.js
    const statusDescriptions = {
        '200': 'OK',
        '201': 'Created',
        '204': 'No Content',
        '400': 'Bad Request',
        '401': 'Unauthorized',
        '403': 'Forbidden',
        '404': 'Not Found',
        '422': 'Validation Error',
        '500': 'Internal Server Error',
        '502': 'Bad Gateway',
        '503': 'Service Unavailable',
        '504': 'Gateway Timeout'
    };
    
    // Ensure 403 is in the responses if not already present
    const responsesObj = { ...operation.responses };
    if (!responsesObj['403']) {
        responsesObj['403'] = {
            description: 'Forbidden'
        };
    }
    
    const responses = Object.entries(responsesObj).map(([code, response]) => {
        const description = response.description || statusDescriptions[code] || 'No description';
        let schema = response.content?.['application/json']?.schema;
        let example = response.content?.['application/json']?.example;
        
        if (schema && state.openApiSpec) {
            schema = resolveSchemaRefs(schema, state.openApiSpec);
            
            if (!example && schema.example) {
                example = schema.example;
            }
            
            if (!example && schema.properties) {
                const exampleObj = {};
                Object.entries(schema.properties).forEach(([key, prop]) => {
                    if (prop.example !== undefined) {
                        exampleObj[key] = prop.example;
                    }
                });
                if (Object.keys(exampleObj).length > 0) {
                    example = exampleObj;
                }
            }
        }
        
        const schemaJson = schema ? JSON.stringify(schema, null, 2) : 'No schema defined';
        
        // Generate example from schema if no explicit example is provided
        let exampleJson;
        if (example) {
            exampleJson = stringifyPreservingOrder(example, 2);
        } else if (schema) {
            const generatedExample = generateSchemaTemplate(schema, state.openApiSpec);
            exampleJson = stringifyPreservingOrder(generatedExample, 2);
        } else {
            exampleJson = 'No example defined';
        }
        
        const hasContent = schema || example;
        const uniqueId = `response-${code}-${Math.random().toString(36).substr(2, 9)}`;
        
        return `
            <div class="response-item-wrapper" data-response-id="${uniqueId}">
                <div class="response-item">
                    <span class="action-method method-${code.startsWith('2') ? 'get' : 'delete'}">${code}</span>
                    <span class="response-desc">${description}</span>
                </div>
                ${hasContent ? `
                    <div class="response-toggle-container">
                        <button class="response-toggle-btn active" onclick="toggleResponseView('${uniqueId}', 'example')">
                            <span class="material-icons">code</span>
                            Example
                        </button>
                        <button class="response-toggle-btn" onclick="toggleResponseView('${uniqueId}', 'schema')">
                            <span class="material-icons">description</span>
                            Schema
                        </button>
                    </div>
                    <pre class="response-display response-example active">${exampleJson}</pre>
                    <pre class="response-display response-schema">${schemaJson}</pre>
                ` : ''}
            </div>
        `;
    }).join('');
    
    return `
        <div class="collapsible-section">
            <div class="collapsible-header" onclick="toggleCollapsible(this)">
                <span class="material-icons collapsible-icon">chevron_right</span>
                <span>Response Info</span>
            </div>
            <div class="collapsible-content collapsed">
                ${responses}
            </div>
        </div>
    `;
}

window.toggleResponseView = function(responseId, view) {
    const container = document.querySelector(`[data-response-id="${responseId}"]`);
    if (!container) return;
    
    const buttons = container.querySelectorAll('.response-toggle-btn');
    const displays = container.querySelectorAll('.response-display');
    
    buttons.forEach(btn => btn.classList.remove('active'));
    displays.forEach(display => display.classList.remove('active'));
    
    const clickedButton = Array.from(buttons).find(btn => 
        btn.textContent.toLowerCase().includes(view)
    );
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
    
    const targetDisplay = container.querySelector(`.response-${view}`);
    if (targetDisplay) {
        targetDisplay.classList.add('active');
    }
};
