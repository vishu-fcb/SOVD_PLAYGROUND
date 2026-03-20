export function decodeJWT(token) {
    if (!token) return null;
    
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        
        const payload = parts[1];
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
}

export function extractRoleFromToken(token) {
    const payload = decodeJWT(token);
    if (!payload) return null;
    
    if (payload.role) return payload.role;
    if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
        return payload.roles[0];
    }
    if (payload.authorization_details && Array.isArray(payload.authorization_details)) {
        const authDetail = payload.authorization_details[0];
        if (authDetail && authDetail.roles && Array.isArray(authDetail.roles) && authDetail.roles.length > 0) {
            return authDetail.roles[0];
        }
    }
    
    return null;
}

export function getAppIcon(appName) {
    const iconMap = {
        'health-monitoring': 'monitor_heart',
        'ac-control': 'ac_unit',
        'light-control': 'lightbulb',
        'light-control-kuksa': 'lightbulb'
    };
    return iconMap[appName] || 'apps';
}

export function formatJson(index) {
    const textarea = document.getElementById(`body-${index}`);
    if (!textarea) return;

    try {
        const parsed = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(parsed, null, 2);
    } catch (e) {
        alert('Invalid JSON: ' + e.message);
    }
}
window.formatJson = formatJson;
