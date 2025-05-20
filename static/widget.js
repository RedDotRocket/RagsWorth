/**
 * RagsWorth Widget - A sleek chatbot widget for embedding in websites.
 */

class RagsWorth {
    constructor(config) {
        this.config = {
            endpoint: 'http://localhost:8000',
            containerId: 'ragsworth-chat',
            theme: {
                primary: '#2563eb',
                secondary: '#4b5563',
                background: '#ffffff',
                text: '#1f2937',
                lightGray: '#f3f4f6',
                borderRadius: '12px',
                accentShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.1), 0 2px 4px -1px rgba(37, 99, 235, 0.06)'
            },
            botName: 'RagsWorth',
            showAvatar: true,
            ...config
        };

        this.sessionId = this._generateSessionId();
        this.context = [];
        this.isTyping = false;

        this._init();
    }

    _generateSessionId() {
        return 'session_' + Math.random().toString(36).substring(2);
    }

    _init() {
        // Create container
        this.container = document.getElementById(this.config.containerId);
        if (!this.container) {
            throw new Error(`Container #${this.config.containerId} not found`);
        }

        // Add styles
        this._addStyles();

        // Create chat interface
        this.container.innerHTML = `
            <div class="ragsworth-widget">
                <div class="ragsworth-header">
                    <div class="ragsworth-avatar">
                        ${this.config.showAvatar ? '<div class="avatar-icon">R</div>' : ''}
                    </div>
                    <div class="ragsworth-title">${this.config.botName}</div>
                </div>
                <div class="ragsworth-messages"></div>
                <div class="ragsworth-input">
                    <textarea placeholder="Type your message..." rows="1"></textarea>
                    <button>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        // Add event listeners
        this._addEventListeners();

        // Add welcome message
        this._addMessage('bot', 'Hello! How can I help you today?');
    }

    _addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .ragsworth-widget {
                display: flex;
                flex-direction: column;
                height: 100%;
                min-height: 450px;
                border-radius: ${this.config.theme.borderRadius};
                background: ${this.config.theme.background};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                overflow: hidden;
                transition: all 0.3s ease;
                position: relative;
            }
            
            .ragsworth-header {
                display: flex;
                align-items: center;
                padding: 1rem;
                background: ${this.config.theme.primary};
                color: white;
                font-weight: 600;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }
            
            .ragsworth-avatar {
                margin-right: 0.75rem;
            }
            
            .avatar-icon {
                width: 32px;
                height: 32px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }
            
            .ragsworth-title {
                font-size: 1.1rem;
            }

            .ragsworth-messages {
                flex: 1;
                overflow-y: auto;
                padding: 1.5rem;
                scroll-behavior: smooth;
                background-color: ${this.config.theme.lightGray};
            }
            
            .ragsworth-messages::-webkit-scrollbar {
                width: 6px;
            }
            
            .ragsworth-messages::-webkit-scrollbar-thumb {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
            }

            .ragsworth-message {
                margin-bottom: 1.25rem;
                max-width: 85%;
                opacity: 0;
                transform: translateY(10px);
                animation: messageAppear 0.3s forwards;
            }
            
            @keyframes messageAppear {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .ragsworth-message.user {
                margin-left: auto;
            }

            .ragsworth-message-content {
                padding: 0.75rem 1rem;
                border-radius: 18px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                position: relative;
                line-height: 1.5;
            }

            .ragsworth-message.bot .ragsworth-message-content {
                background: ${this.config.theme.background};
                color: ${this.config.theme.text};
                border-bottom-left-radius: 4px;
            }

            .ragsworth-message.user .ragsworth-message-content {
                background: ${this.config.theme.primary};
                color: white;
                border-bottom-right-radius: 4px;
                box-shadow: ${this.config.theme.accentShadow};
            }
            
            .ragsworth-message.bot .ragsworth-message-content::before {
                content: '';
                position: absolute;
                left: -6px;
                bottom: 0;
                width: 12px;
                height: 12px;
                background: ${this.config.theme.background};
                clip-path: polygon(100% 0, 100% 100%, 0 100%);
            }
            
            .ragsworth-message.user .ragsworth-message-content::before {
                content: '';
                position: absolute;
                right: -6px;
                bottom: 0;
                width: 12px;
                height: 12px;
                background: ${this.config.theme.primary};
                clip-path: polygon(0 0, 100% 100%, 0 100%);
            }

            .ragsworth-sources {
                font-size: 0.8rem;
                margin-top: 0.75rem;
                color: ${this.config.theme.secondary};
                padding: 0.5rem 0.75rem;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
                border-left: 3px solid ${this.config.theme.primary};
            }
            
            .ragsworth-sources-title {
                font-weight: 600;
                margin-bottom: 0.25rem;
            }

            .ragsworth-input {
                display: flex;
                padding: 1rem;
                background: ${this.config.theme.background};
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            }

            .ragsworth-input textarea {
                flex: 1;
                padding: 0.75rem 1rem;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: ${this.config.theme.borderRadius};
                margin-right: 0.75rem;
                resize: none;
                font-family: inherit;
                font-size: 0.95rem;
                line-height: 1.5;
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s;
                max-height: 120px;
                overflow-y: auto;
            }
            
            .ragsworth-input textarea:focus {
                border-color: ${this.config.theme.primary};
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
            }

            .ragsworth-input button {
                width: 40px;
                height: 40px;
                background: ${this.config.theme.primary};
                color: white;
                border: none;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                box-shadow: ${this.config.theme.accentShadow};
                align-self: flex-end;
            }

            .ragsworth-input button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 10px -1px rgba(37, 99, 235, 0.2);
            }

            .ragsworth-input button:active {
                transform: translateY(0);
                box-shadow: ${this.config.theme.accentShadow};
            }

            .ragsworth-input button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: translateY(0);
            }
            
            .typing-indicator {
                display: flex;
                padding: 15px 12px;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 50%;
                margin: 0 2px;
                animation: typingDot 1.4s infinite;
                display: inline-block;
            }
            
            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }
            
            @keyframes typingDot {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-5px); }
            }
        `;

        document.head.appendChild(style);
    }

    _addEventListeners() {
        const textarea = this.container.querySelector('textarea');
        const button = this.container.querySelector('button');

        // Send on button click
        button.addEventListener('click', () => this._sendMessage());

        // Send on Enter (but allow Shift+Enter for new lines)
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this._sendMessage();
            }
        });
        
        // Auto-resize textarea
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight > 120 ? 120 : textarea.scrollHeight) + 'px';
        });
    }

    async _sendMessage() {
        const textarea = this.container.querySelector('textarea');
        const button = this.container.querySelector('button');
        const message = textarea.value.trim();

        if (!message) return;

        // Disable input while processing
        textarea.disabled = true;
        button.disabled = true;

        // Add user message
        this._addMessage('user', message);
        
        // Show typing indicator
        this._showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch(`${this.config.endpoint}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_message: message,
                    context: this.context
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            
            // Remove typing indicator
            this._hideTypingIndicator();

            // Add bot response with sources
            this._addMessage('bot', data.bot_reply, data.source_documents);

            // Update context
            this.context.push(
                { role: 'user', content: message },
                { role: 'assistant', content: data.bot_reply }
            );

            // Keep context size manageable
            if (this.context.length > 10) {
                this.context = this.context.slice(-10);
            }

        } catch (error) {
            console.error('Error:', error);
            this._hideTypingIndicator();
            this._addMessage('bot', 'Sorry, something went wrong. Please try again.');
        }

        // Clear and re-enable input
        textarea.value = '';
        textarea.style.height = 'auto';
        textarea.disabled = false;
        button.disabled = false;
        textarea.focus();
    }
    
    _showTypingIndicator() {
        const messages = this.container.querySelector('.ragsworth-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ragsworth-message bot typing';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ragsworth-message-content typing-indicator';
        contentDiv.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        
        typingDiv.appendChild(contentDiv);
        messages.appendChild(typingDiv);
        messages.scrollTop = messages.scrollHeight;
        
        this.isTyping = true;
    }
    
    _hideTypingIndicator() {
        const typing = this.container.querySelector('.typing');
        if (typing) {
            typing.remove();
        }
        this.isTyping = false;
    }

    _addMessage(role, content, sources = []) {
        const messages = this.container.querySelector('.ragsworth-messages');

        const messageDiv = document.createElement('div');
        messageDiv.className = `ragsworth-message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'ragsworth-message-content';
        contentDiv.textContent = content;
        messageDiv.appendChild(contentDiv);

        // Add sources if available
        if (sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'ragsworth-sources';
            sourcesDiv.innerHTML = `
                <div class="ragsworth-sources-title">Sources:</div>
                ${sources.map(s => `<div>${s.snippet}</div>`).join('')}
            `;
            messageDiv.appendChild(sourcesDiv);
        }

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
}