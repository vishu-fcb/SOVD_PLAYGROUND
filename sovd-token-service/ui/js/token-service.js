const CONFIG_PRESETS = {
    'oem-developer': {
        user_id: 'user:admin001',
        vin: '*',
        issuer: 'https://auth.oem.example.com',
        audience: 'sovd-api',
        roles: 'oem_developer',
        actions: 'sovd:meta:read, sovd:logs:read, sovd:logs:write, sovd:configuration:read, sovd:configuration:write, sovd:data:read, sovd:data:write, sovd:faults:read, sovd:faults:write, sovd:operations:read, sovd:operations:exec, sovd:health-monitoring:read',
        expires_in: 7200
    },
    'workshop-technician': {
        user_id: 'user:tech123',
        vin: 'WVWZZZ1JZXW000000',
        issuer: 'https://auth.oem.example.com',
        audience: 'sovd-api',
        roles: 'workshop_technician',
        actions: 'sovd:meta:read, sovd:logs:read, sovd:configuration:read, sovd:configuration:write, sovd:data:read, sovd:data:write, sovd:faults:read, sovd:operations:read, sovd:operations:exec, sovd:health-monitoring:read',
        expires_in: 3600
    },
    'vehicle-monitoring': {
        user_id: 'user:fleet789',
        vin: 'WVWZZZ1JZXW000000',
        issuer: 'https://auth.oem.example.com',
        audience: 'sovd-api',
        roles: 'vehicle_monitoring',
        actions: 'sovd:meta:read, sovd:logs:read, sovd:configuration:read, sovd:data:read, sovd:faults:read, sovd:operations:read, sovd:health-monitoring:read',
        expires_in: 3600
    },
    'read-only': {
        user_id: 'user:readonly',
        vin: 'WVWZZZ1JZXW000000',
        issuer: 'https://auth.oem.example.com',
        audience: 'sovd-api',
        roles: 'generic',
        actions: 'sovd:meta:read',
        expires_in: 1800
    },
    'custom': {
        user_id: 'user:custom',
        vin: 'WVWZZZ1JZXW000000',
        issuer: 'https://auth.oem.example.com',
        audience: 'sovd-api',
        roles: 'custom',
        actions: 'sovd:meta:read',
        expires_in: 3600
    }
};
function decodeJWT(token) {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) {
            throw new Error('Invalid JWT format');
        }
        
        const payload = parts[1];
        const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
        return JSON.parse(decoded);
    } catch (error) {
        console.error('Failed to decode JWT:', error);
        return null;
    }
}
function loadConfig(configName) {
    const config = CONFIG_PRESETS[configName];
    if (!config) return;
    
    document.getElementById('user-id').value = config.user_id;
    document.getElementById('vin').value = config.vin;
    document.getElementById('issuer').value = config.issuer;
    document.getElementById('audience').value = config.audience;
    document.getElementById('roles').value = config.roles;
    document.getElementById('actions').value = config.actions;
    document.getElementById('expires-in').value = config.expires_in;
    
    document.querySelectorAll('.config-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector(`[data-config="${configName}"]`).classList.add('active');
    
    showNotification(`Loaded: ${document.querySelector(`[data-config="${configName}"] .config-title`).textContent}`, 'success');
}
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
async function generateToken() {
    const generateBtn = document.getElementById('generate-btn');
    const userId = document.getElementById('user-id').value.trim();
    const vin = document.getElementById('vin').value.trim();
    const issuer = document.getElementById('issuer').value.trim();
    const audience = document.getElementById('audience').value.trim();
    const rolesInput = document.getElementById('roles').value.trim();
    const actionsInput = document.getElementById('actions').value.trim();
    const expiresIn = parseInt(document.getElementById('expires-in').value);
    
    if (!userId || !vin || !issuer || !audience || !rolesInput || !actionsInput || !expiresIn) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    const roles = rolesInput.split(',').map(r => r.trim()).filter(r => r);
    const actions = actionsInput.split(',').map(a => a.trim()).filter(a => a);
    
    const requestBody = {
        user_id: userId,
        vin: vin,
        issuer: issuer,
        audience: audience,
        roles: roles,
        actions: actions,
        expires_in: expiresIn
    };
    
    generateBtn.disabled = true;
    const originalContent = generateBtn.innerHTML;
    generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate token');
        }
        
        const data = await response.json();
        const token = data.access_token;
        
        const tokenDisplay = document.getElementById('token-display');
        tokenDisplay.textContent = token;
        document.getElementById('token-card').style.display = 'block';
        
        setTimeout(() => {
            document.getElementById('token-card').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }, 100);
        
        const decoded = decodeJWT(token);
        if (decoded) {
            document.getElementById('decoded-payload').textContent = JSON.stringify(decoded, null, 2);
            document.getElementById('decoded-card').style.display = 'block';
        }
        
        showNotification('Token generated successfully! Click token to copy.', 'success');
        
    } catch (error) {
        console.error('Error generating token:', error);
        showNotification(error.message || 'Failed to generate token', 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalContent;
    }
}
async function copyToken() {
    const tokenDisplay = document.getElementById('token-display');
    const token = tokenDisplay.textContent;
    
    try {
        await navigator.clipboard.writeText(token);
        showNotification('Token copied to clipboard!', 'success');
        
        const copyBtn = document.getElementById('copy-token-btn');
        if (copyBtn) {
            const icon = copyBtn.querySelector('.material-icons');
            const originalText = icon.textContent;
            icon.textContent = 'check';
            setTimeout(() => {
                icon.textContent = originalText;
            }, 2000);
        }
    } catch (error) {
        console.error('Failed to copy token:', error);
        showNotification('Failed to copy token', 'error');
    }
}
async function copyPayload() {
    const payloadElement = document.getElementById('decoded-payload');
    const payload = payloadElement.textContent;
    
    try {
        await navigator.clipboard.writeText(payload);
        showNotification('Payload JSON copied to clipboard!', 'success');
        
        const copyBtn = document.getElementById('copy-payload-btn');
        if (copyBtn) {
            const icon = copyBtn.querySelector('.material-icons');
            const originalText = icon.textContent;
            icon.textContent = 'check';
            setTimeout(() => {
                icon.textContent = originalText;
            }, 2000);
        }
    } catch (error) {
        console.error('Failed to copy payload:', error);
        showNotification('Failed to copy payload', 'error');
    }
}
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const detailsHeader = document.getElementById('details-header');
    const detailsContent = document.getElementById('details-content');
    
    if (detailsHeader && detailsContent) {
        detailsHeader.addEventListener('click', () => {
            const expandIcon = detailsHeader.querySelector('.expand-icon');
            const isCollapsed = detailsContent.classList.contains('collapsed');
            
            if (isCollapsed) {
                detailsContent.classList.remove('collapsed');
                detailsContent.classList.add('expanded');
                if (expandIcon) {
                    expandIcon.classList.add('expanded');
                }
            } else {
                detailsContent.classList.remove('expanded');
                detailsContent.classList.add('collapsed');
                if (expandIcon) {
                    expandIcon.classList.remove('expanded');
                }
            }
        });
    }
    
    generateBtn.addEventListener('click', generateToken);
    
    document.addEventListener('click', (e) => {
        if (e.target.closest('#copy-token-btn')) {
            copyToken();
        }
        if (e.target.closest('#copy-payload-btn')) {
            copyPayload();
        }
        if (e.target.id === 'token-display') {
            copyToken();
        }
    });
    
    document.querySelectorAll('.config-card').forEach(card => {
        card.addEventListener('click', () => {
            const configName = card.getAttribute('data-config');
            loadConfig(configName);
        });
    });
    
    const inputs = document.querySelectorAll('.input-field input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            document.querySelectorAll('.config-card').forEach(card => {
                card.classList.remove('active');
            });
            const customCard = document.querySelector('[data-config="custom"]');
            if (customCard) {
                customCard.classList.add('active');
            }
        });
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                generateToken();
            }
        });
    });
    
    loadConfig('workshop-technician');
});
