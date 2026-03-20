export const state = {
    gatewayUrl: localStorage.getItem('sovd-gateway-url') || 'http://localhost:8080',
    chatUrl: localStorage.getItem('sovd-chat-url') || '',
    accessToken: localStorage.getItem('sovd-access-token') || '',
    connected: false,
    openApiSpec: null,
    apps: [],
    currentApp: null,
    searchResults: []
};

export const urlParams = new URLSearchParams(window.location.search);