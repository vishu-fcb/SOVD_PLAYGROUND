import { state } from './state.js';
import { connectToGateway, refreshDocs, updateConnectionStatus, updateMainPanel } from './api.js';
import { parseAppsFromSpec, renderApps, selectApp } from './ui.js';
import { performSearch } from './search.js';
import { sendChatMessage, autoResizeTextarea } from './chat.js';
import { executeOperation } from './operations.js';
import { extractRoleFromToken } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const settingsTrigger = document.getElementById('settings-trigger');
    const settingsDropdown = document.getElementById('settings-dropdown');
    const settingsPopup = document.getElementById('settings-popup');
    const settingsSaveBtn = document.getElementById('settings-save-btn');

    document.getElementById('gateway-url').value = state.gatewayUrl;
    document.getElementById('chat-url').value = state.chatUrl;
    document.getElementById('access-token').value = state.accessToken || '';

    function updateRoleChip() {
        const roleChip = document.getElementById('role-chip');
        const roleText = document.getElementById('role-text');
        
        if (!roleChip || !roleText) return;
        
        if (state.accessToken && state.accessToken.trim()) {
            const role = extractRoleFromToken(state.accessToken);
            if (role) {
                roleText.textContent = role;
                roleChip.style.display = 'inline-flex';
            } else {
                roleChip.style.display = 'none';
            }
        } else {
            roleChip.style.display = 'none';
        }
    }

    try {
        updateRoleChip();
    } catch (error) {
        console.error('Error updating role chip:', error);
    }

    settingsTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        settingsDropdown.classList.toggle('show');
    });

    settingsSaveBtn.addEventListener('click', async () => {
        const gatewayUrl = document.getElementById('gateway-url').value.trim();
        const chatUrl = document.getElementById('chat-url').value.trim();
        const accessToken = document.getElementById('access-token').value.trim();

        if (!gatewayUrl) {
            alert('Please enter a Gateway URL');
            return;
        }

        state.gatewayUrl = gatewayUrl;
        localStorage.setItem('sovd-gateway-url', gatewayUrl);

        state.chatUrl = chatUrl;
        localStorage.setItem('sovd-chat-url', chatUrl);

        state.accessToken = accessToken;
        localStorage.setItem('sovd-access-token', accessToken);

        try {
            updateRoleChip();
        } catch (error) {
            console.error('Error updating role chip:', error);
        }

        settingsSaveBtn.disabled = true;
        const originalContent = settingsSaveBtn.innerHTML;
        settingsSaveBtn.innerHTML = '<span class="spinner"></span> Connecting...';

        try {
            await connectToGateway();
        } catch (error) {
            console.error('Save & Connect error:', error);
        } finally {
            settingsSaveBtn.disabled = false;
            settingsSaveBtn.innerHTML = originalContent;
        }
    });

    document.addEventListener('click', (e) => {
        if (settingsPopup && !settingsPopup.contains(e.target)) {
            settingsDropdown.classList.remove('show');
        }
    });

    document.getElementById('refresh-btn').addEventListener('click', refreshDocs);
    document.getElementById('chat-send').addEventListener('click', sendChatMessage);
    
    // Chat input with auto-resize (VS Code style)
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('input', autoResizeTextarea);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // Chat panel toggle functionality
    const chatPanel = document.getElementById('chat-panel');
    const chatToggle = document.getElementById('chat-toggle');
    const chatClose = document.getElementById('chat-close');
    const chatResizeHandle = document.getElementById('chat-resize-handle');
    
    // Chat panel resize functionality
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    const minWidth = 320;
    const maxWidth = 800;
    
    chatResizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startWidth = chatPanel.offsetWidth;
        chatResizeHandle.classList.add('resizing');
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        
        const diff = startX - e.clientX;
        let newWidth = startWidth + diff;
        newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
        
        chatPanel.style.width = newWidth + 'px';
        chatPanel.style.minWidth = newWidth + 'px';
    });
    
    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            chatResizeHandle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            
            // Save the width
            localStorage.setItem('sovd-chat-width', chatPanel.offsetWidth);
        }
    });
    
    // Restore saved chat panel width (only if not collapsed)
    const savedWidth = localStorage.getItem('sovd-chat-width');
    const chatCollapsed = localStorage.getItem('sovd-chat-collapsed');
    if (savedWidth && chatCollapsed !== 'true') {
        const width = parseInt(savedWidth);
        if (width >= minWidth && width <= maxWidth) {
            chatPanel.style.width = width + 'px';
            chatPanel.style.minWidth = width + 'px';
        }
    }
    
    chatToggle.addEventListener('click', () => {
        chatPanel.classList.remove('collapsed');
        // Restore saved width when opening
        const savedWidth = localStorage.getItem('sovd-chat-width');
        if (savedWidth) {
            chatPanel.style.width = savedWidth + 'px';
            chatPanel.style.minWidth = savedWidth + 'px';
        }
        localStorage.setItem('sovd-chat-collapsed', 'false');
    });
    
    chatClose.addEventListener('click', () => {
        chatPanel.classList.add('collapsed');
        // Clear inline width styles to let CSS width:0 take effect
        chatPanel.style.width = '';
        chatPanel.style.minWidth = '';
        localStorage.setItem('sovd-chat-collapsed', 'true');
    });
    
    if (chatCollapsed === 'false') {
        chatPanel.classList.remove('collapsed');
    }

    document.getElementById('global-search-input').addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        performSearch(searchTerm);
    });

    document.querySelector('.sidebar').addEventListener('click', (e) => {
        const appItem = e.target.closest('.app-item');
        if (appItem) {
            const appName = appItem.dataset.app;
            selectApp(appName);
        }
    });

    updateMainPanel();
});

window.executeOperation = executeOperation;