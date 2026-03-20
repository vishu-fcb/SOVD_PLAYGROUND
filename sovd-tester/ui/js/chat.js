import { state } from './state.js';

function getChatId() {
    let chatId = sessionStorage.getItem("chatId");
    if (!chatId) {
        chatId = "chat_" + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem("chatId", chatId);
    }
    return chatId;
}

function parseMarkdown(text) {
    if (!text) return '';
    
    let html = text;
    
    html = html.replace(/[<>&"']/g, function(match) {
        const escape = {
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return escape[match];
    });
    
    // Headers (# ## ###)
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Bold (**text**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic (*text*)
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Inline code (`code`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Code blocks (```code```)
    html = html.replace(/```([^`]+)```/gs, '<pre><code>$1</code></pre>');
    
    // Process lists line by line to handle mixed numbered/bullet lists
    const lines = html.split('\n');
    const processedLines = [];
    let inList = false;
    let listType = null;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();
        
        // Check for numbered list items (1. 2. 3. etc.)
        const numberedMatch = trimmedLine.match(/^(\d+)\.\s+(.+)$/);
        if (numberedMatch) {
            if (!inList || listType !== 'ol') {
                if (inList) processedLines.push(`</${listType}>`);
                processedLines.push('<ol>');
                listType = 'ol';
                inList = true;
            }
            processedLines.push(`<li>${numberedMatch[2]}</li>`);
            continue;
        }
        
        // Check for bullet list items (- or • or *)
        const bulletMatch = trimmedLine.match(/^[-•*]\s+(.+)$/);
        if (bulletMatch) {
            if (!inList || listType !== 'ul') {
                if (inList) processedLines.push(`</${listType}>`);
                processedLines.push('<ul>');
                listType = 'ul';
                inList = true;
            }
            processedLines.push(`<li>${bulletMatch[1]}</li>`);
            continue;
        }
        
        // Not a list item
        if (inList) {
            processedLines.push(`</${listType}>`);
            inList = false;
            listType = null;
        }
        
        // Handle empty lines and regular text
        if (trimmedLine === '') {
            processedLines.push('');
        } else {
            processedLines.push(line);
        }
    }
    
    // Close any open list
    if (inList) {
        processedLines.push(`</${listType}>`);
    }
    
    html = processedLines.join('\n');
    
    // Links [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Paragraphs (double line breaks)
    const paragraphs = html.split(/\n\s*\n/);
    html = paragraphs.map(p => {
        p = p.trim();
        if (!p) return '';
        // Don't wrap if already contains block elements
        if (p.includes('<h1>') || p.includes('<h2>') || p.includes('<h3>') || 
            p.includes('<ul>') || p.includes('<ol>') || p.includes('<pre>') ||
            p.includes('<div>')) {
            return p;
        }
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).filter(p => p).join('\n');
    
    return html;
}

function formatChatResponse(text) {
    if (!text) return '';
    return parseMarkdown(text);
}

export function autoResizeTextarea() {
    const input = document.getElementById('chat-input');
    if (!input) return;
    
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 200) + 'px';
}

export function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const chatMessages = document.getElementById('chat-messages');

    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.textContent = message;
    chatMessages.appendChild(userMsg);

    input.value = '';
    input.style.height = 'auto'; // Reset height after sending
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add typing indicator
    const typingMsg = document.createElement('div');
    typingMsg.className = 'chat-message assistant typing';
    typingMsg.innerHTML = '<span class="typing-indicator"></span><span class="typing-indicator"></span><span class="typing-indicator"></span>';
    chatMessages.appendChild(typingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Use webhook if URL is set
    if (state.chatUrl) {
        const chatId = getChatId(); // Get the chat ID
        
        fetch(state.chatUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                chatId: chatId, // Reverted back to chatId
                message: message, 
                route: 'general' 
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            typingMsg.remove();
            
            const assistantMsg = document.createElement('div');
            assistantMsg.className = 'chat-message assistant';
            assistantMsg.style.opacity = '0';
            
            // Try different response field names that n8n might use
            const reply = data.reply || data.output || data.response || data.message || 'Received, but no reply content.';
            
            // Format the response text for better readability
            assistantMsg.innerHTML = formatChatResponse(reply);
            chatMessages.appendChild(assistantMsg);
            
            // Fade in animation
            setTimeout(() => {
                assistantMsg.style.transition = 'opacity 0.4s ease';
                assistantMsg.style.opacity = '1';
            }, 10);
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            console.error('Chat webhook error:', error);
            
            // Remove typing indicator
            typingMsg.remove();
            
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message assistant';
            errorMsg.textContent = 'Error connecting to AI assistant: ' + error.message;
            chatMessages.appendChild(errorMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    } else {
        // Fallback echo response
        setTimeout(() => {
            // Remove typing indicator
            typingMsg.remove();
            
            const assistantMsg = document.createElement('div');
            assistantMsg.className = 'chat-message assistant';
            assistantMsg.style.opacity = '0';
            
            const fallbackText = 'I received your message: "' + message + '". Configure the webhook URL to enable the AI assistant.';
            assistantMsg.innerHTML = formatChatResponse(fallbackText);
            chatMessages.appendChild(assistantMsg);
            
            // Fade in animation
            setTimeout(() => {
                assistantMsg.style.transition = 'opacity 0.4s ease';
                assistantMsg.style.opacity = '1';
            }, 10);
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);
    }
}
