/**
 * MS College Campus Events - AI Chat Widget
 * Floating chat button with expandable window
 */

document.addEventListener('DOMContentLoaded', function () {
  const chatToggle  = document.getElementById('aiChatToggle');
  const chatWindow  = document.getElementById('aiChatWindow');
  const chatClose   = document.getElementById('aiChatClose');
  const chatClear   = document.getElementById('aiChatClear');
  const chatInput   = document.getElementById('aiChatInput');
  const chatSendBtn = document.getElementById('aiChatSend');
  const messagesEl  = document.getElementById('aiMessages');

  if (!chatToggle || !chatWindow) return;

  let isOpen    = false;
  let isLoading = false;

  // ── Open / Close ──
  chatToggle.addEventListener('click', () => {
    isOpen = !isOpen;
    chatWindow.classList.toggle('open', isOpen);
    chatToggle.innerHTML = isOpen
      ? '<i class="fa-solid fa-xmark"></i>'
      : '<i class="fa-solid fa-robot"></i>';
    if (isOpen && messagesEl.children.length === 0) {
      addBotMessage(getGreeting());
    }
    if (isOpen && chatInput) chatInput.focus();
  });

  if (chatClose) {
    chatClose.addEventListener('click', () => {
      isOpen = false;
      chatWindow.classList.remove('open');
      chatToggle.innerHTML = '<i class="fa-solid fa-robot"></i>';
    });
  }

  // ── Clear chat ──
  if (chatClear) {
    chatClear.addEventListener('click', () => {
      if (messagesEl) messagesEl.innerHTML = '';
      addBotMessage(getGreeting());
    });
  }

  // ── Send message ──
  function sendMessage() {
    if (isLoading) return;
    const message = chatInput?.value?.trim();
    if (!message) return;

    addUserMessage(message);
    chatInput.value = '';
    showTyping();
    isLoading = true;

    // Detect language from langManager
    const lang = window.langManager ? window.langManager.lang : 'en';

    fetch('/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        lang,
        user_id: window.currentUserId || null,
      }),
    })
    .then(r => {
      if (!r.ok) throw new Error('Server error');
      return r.json();
    })
    .then(data => {
      hideTyping();
      isLoading = false;
      addBotMessage(data.response || data.reply || 'Sorry, I could not process that.');
    })
    .catch(() => {
      hideTyping();
      isLoading = false;
      const errMsg = lang === 'ta'
        ? 'மன்னிக்கவும், இப்போது பதில் சொல்ல முடியவில்லை.'
        : 'Sorry, I am unable to respond right now. Please try again.';
      addBotMessage(errMsg);
    });
  }

  if (chatSendBtn) {
    chatSendBtn.addEventListener('click', sendMessage);
  }

  if (chatInput) {
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Update placeholder on language change
    document.addEventListener('languageChanged', ({ detail }) => {
      const key = 'ai.placeholder';
      const lang = detail.lang;
      if (window.translations && window.translations[lang]) {
        chatInput.placeholder = window.translations[lang][key] || chatInput.placeholder;
      }
    });
  }

  // ── Message renderers ──
  function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'ai-message user';
    div.innerHTML = `
      <div class="ai-message-bubble">${escapeHtml(text)}</div>
      <div class="ai-message-icon" style="background:var(--gradient-red)">
        <i class="fa-solid fa-user"></i>
      </div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
  }

  function addBotMessage(text) {
    const div = document.createElement('div');
    div.className = 'ai-message bot';
    div.innerHTML = `
      <div class="ai-message-icon">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="ai-message-bubble">${formatBotMessage(text)}</div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
  }

  let typingEl = null;

  function showTyping() {
    hideTyping();
    typingEl = document.createElement('div');
    typingEl.className = 'ai-message bot';
    typingEl.id = 'aiTypingIndicator';
    typingEl.innerHTML = `
      <div class="ai-message-icon">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="ai-typing">
        <span></span><span></span><span></span>
      </div>
    `;
    messagesEl.appendChild(typingEl);
    scrollToBottom();
  }

  function hideTyping() {
    if (typingEl && typingEl.isConnected) typingEl.remove();
    typingEl = null;
  }

  function scrollToBottom() {
    if (messagesEl) {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }
  }

  // ── Helpers ──
  function getGreeting() {
    const lang = window.langManager ? window.langManager.lang : 'en';
    const hour = new Date().getHours();
    const timeGreet = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
    const userName  = window.currentUserName || '';

    if (lang === 'ta') {
      return `வணக்கம்${userName ? ' ' + userName : ''}! நான் MS வளாக AI உதவியாளர். நிகழ்வுகள், பதிவுகள் அல்லது சான்றிதழ்கள் பற்றி கேளுங்கள்! 🎓`;
    }
    return `${timeGreet}${userName ? ', ' + userName : ''}! I'm the MS Campus AI Assistant. Ask me about events, registrations, or certificates! 🎓`;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatBotMessage(text) {
    // Convert **bold** and *italic* and line breaks
    return escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  // ── Keyboard shortcut: Ctrl+/ to open chat ──
  document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.key === '/') {
      e.preventDefault();
      chatToggle.click();
    }
  });

  // ── Unread indicator ──
  let unreadCount = 0;

  function showUnread() {
    unreadCount++;
    let badge = chatToggle.querySelector('.chat-unread-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'chat-unread-badge';
      badge.style.cssText = `
        position: absolute;
        top: -4px; right: -4px;
        background: #fff; color: var(--accent-red);
        border-radius: 50%;
        width: 20px; height: 20px;
        font-size: 0.7rem; font-weight: 800;
        display: flex; align-items: center; justify-content: center;
        animation: bounceIn 0.4s ease;
      `;
      chatToggle.style.position = 'relative';
      chatToggle.appendChild(badge);
    }
    badge.textContent = unreadCount;
  }

  function clearUnread() {
    unreadCount = 0;
    const badge = chatToggle.querySelector('.chat-unread-badge');
    if (badge) badge.remove();
  }

  // Show welcome message after 5s if chat is closed
  setTimeout(() => {
    if (!isOpen) {
      showUnread();
    }
  }, 5000);

  chatToggle.addEventListener('click', clearUnread);
});
