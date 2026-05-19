const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message');
const messagesEl = document.getElementById('chat-messages');
const statusEl = document.getElementById('connection-status');
const clearBtn = document.getElementById('clear-chat');
const sendBtn = chatForm.querySelector('.btn-send');

let isBusy = false;

function formatTime(date = new Date()) {
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

function setStatus(mode, text) {
    statusEl.classList.remove('busy', 'error');
    if (mode) statusEl.classList.add(mode);
    statusEl.innerHTML = `<span class="status-dot"></span> ${text}`;
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function addMessage(role, text, options = {}) {
    const { isError = false } = options;
    const isUser = role === 'user';

    const article = document.createElement('article');
    article.className = `message message-${isUser ? 'user' : 'bot'}${isError ? ' message-error' : ''}`;

    const avatar = document.createElement('div');
    avatar.className = `avatar avatar-${isUser ? 'user' : 'bot'}`;
    avatar.setAttribute('aria-hidden', 'true');
    avatar.textContent = isUser ? '★' : 'S';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = `<p>${escapeHtml(text)}</p><time>${formatTime()}</time>`;

    article.appendChild(avatar);
    article.appendChild(bubble);
    messagesEl.appendChild(article);
    scrollToBottom();
    return article;
}

function showTyping() {
    const article = document.createElement('article');
    article.className = 'message message-bot message-typing';
    article.id = 'typing-indicator';
    article.innerHTML = `
        <div class="avatar avatar-bot" aria-hidden="true">S</div>
        <div class="bubble">
            <div class="typing-dots" aria-label="Yazıyor">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messagesEl.appendChild(article);
    scrollToBottom();
}

function hideTyping() {
    document.getElementById('typing-indicator')?.remove();
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 140)}px`;
}

messageInput.addEventListener('input', autoResizeTextarea);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});

chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (isBusy) return;

    const message = messageInput.value.trim();
    if (!message) return;

    addMessage('user', message);
    messageInput.value = '';
    autoResizeTextarea();

    isBusy = true;
    sendBtn.disabled = true;
    setStatus('busy', 'Yanıt hazırlanıyor…');
    showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        hideTyping();

        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            addMessage('bot', `Sunucu beklenmeyen yanıt döndü (HTTP ${response.status}).`, { isError: true });
            setStatus('error', 'Bağlantı hatası');
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            addMessage('bot', data.error || data.response || 'Bir hata oluştu.', { isError: true });
            setStatus('error', 'Hata');
            return;
        }

        addMessage('bot', data.response || 'Yanıt alınamadı.');
        setStatus(null, 'Hazır');
    } catch (error) {
        hideTyping();
        addMessage('bot', `Bağlantı hatası: ${error.message}`, { isError: true });
        setStatus('error', 'Çevrimdışı');
    } finally {
        isBusy = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
});

clearBtn.addEventListener('click', async () => {
    if (isBusy) return;
    if (!confirm('Sohbet geçmişi silinsin mi?')) return;

    try {
        const response = await fetch('/chat/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: 'default_user' }),
        });
        if (response.ok) {
            messagesEl.innerHTML = '';
            addMessage('bot', 'Sohbet temizlendi. Yeni bir konuşmaya başlayabilirsiniz.');
            setStatus(null, 'Hazır');
        }
    } catch {
        addMessage('bot', 'Geçmiş temizlenirken bir hata oluştu.', { isError: true });
    }
});

messageInput.focus();
