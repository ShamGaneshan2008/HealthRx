/* =====================================================
   HealthRx AI — app.js (FINAL FIXED)
===================================================== */

/* ── FORMAT MESSAGE ── */
function formatMessage(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^• (.+)$/gm, '<span style="display:block;padding-left:12px">• $1</span>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

/* ── TIME ── */
function getNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/* ── SEND MESSAGE ── */
function submitSymptoms() {
  const input = document.getElementById('symptomInput');
  const messages = document.getElementById('chatMessages');
  const btn = document.getElementById('sendBtn');

  const text = input.value.trim();
  if (!text) return;

  const userMsg = createMessage('user', text, getNow());
  messages.appendChild(userMsg);

  input.value = '';
  btn.disabled = true;
  scrollMessages();

  const prompts = document.getElementById('quickPrompts');
  if (prompts) prompts.style.display = 'none';

  const thinkingEl = createThinkingIndicator();
  messages.appendChild(thinkingEl);
  scrollMessages();

  fetch("http://127.0.0.1:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: text })
  })
  .then(async res => {
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Server error");
    }

    return data;
  })
  .then(data => {
    thinkingEl.remove();

    const aiMsg = createMessage(
      'ai',
      data.reply || data.response || "No response from AI",
      getNow(),
      "info"
    );

    messages.appendChild(aiMsg);
    btn.disabled = false;
    scrollMessages();
  })
  .catch(err => {
    thinkingEl.remove();

    const errorMsg = createMessage(
      'ai',
      "❌ Backend error: " + err.message,
      getNow(),
      "urgent"
    );

    messages.appendChild(errorMsg);
    btn.disabled = false;
    scrollMessages();

    console.error(err);
  });
}

/* ── CREATE MESSAGE ── */
function createMessage(role, text, time) {
  const div = document.createElement('div');
  div.className = `message ${role === 'user' ? 'user-message' : 'ai-message'}`;

  if (role === 'ai') {
    div.innerHTML = `
      <div class="msg-avatar">⚕</div>
      <div class="msg-content">
        <div class="msg-name">HealthRx AI</div>
        <div class="msg-text">${formatMessage(text)}</div>
        <div class="msg-time">${time}</div>
      </div>`;
  } else {
    div.innerHTML = `
      <div class="msg-content">
        <div class="msg-name" style="text-align:right">You</div>
        <div class="msg-text">${text}</div>
        <div class="msg-time">${time}</div>
      </div>`;
  }

  return div;
}

/* ── THINKING INDICATOR ── */
function createThinkingIndicator() {
  const div = document.createElement('div');
  div.className = 'message ai-message';

  div.innerHTML = `
    <div class="msg-avatar">⚕</div>
    <div class="msg-content">
      <div class="msg-name">HealthRx AI</div>
      <div class="msg-text">Typing...</div>
    </div>`;

  return div;
}

/* ── SCROLL ── */
function scrollMessages() {
  const messages = document.getElementById('chatMessages');
  messages.scrollTop = messages.scrollHeight;
}

/* ── ENTER KEY ── */
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('symptomInput');

  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitSymptoms();
      }
    });
  }
});