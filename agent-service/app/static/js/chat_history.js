const statusEl = document.getElementById("status");
const listEl = document.getElementById("list");
const tidEl = document.getElementById("tid");
const messagesEl = document.getElementById("messages");

// 👇 БАЗОВЫЙ URL ДЛЯ API (напрямую к agent-service)
const API_BASE = "http://localhost:8001/api/v1";

function setStatus(text) {
  statusEl.textContent = text;
}

// Проверка авторизации
const user = localStorage.getItem('user');
if (!user) {
  window.location.href = '/ui/login';
}

async function api(path, opts = {}) {
  try {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData && userData.email && userData.api_key) {
      const credentials = btoa(`${userData.email}:${userData.api_key}`);
      opts.headers = {
        ...opts.headers,
        'Authorization': `Basic ${credentials}`
      };
    }

    // 👇 ИСПРАВЛЕНО: используем API_BASE вместо относительного пути
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, opts);
    
    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await res.text();
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${text}`);
      }
      return text ? { message: text } : {};
    }
    
    const data = await res.json();
    
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('user');
        window.location.href = '/ui/login';
        return;
      }
      throw new Error((data && (data.detail || data.message)) || `HTTP ${res.status}`);
    }
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

async function refresh() {
  setStatus("Загрузка...");
  listEl.innerHTML = "";
  try {
    const data = await api("/admin/chat-histories");
    setStatus(`Найдено: ${data.count}`);
    for (const id of data.telegram_ids) {
      const tr = document.createElement("tr");

      const td1 = document.createElement("td");
      td1.textContent = id;

      const td2 = document.createElement("td");
      const viewBtn = document.createElement("button");
      viewBtn.textContent = "Показать";
      viewBtn.onclick = () => loadHistory(id);

      const delBtn = document.createElement("button");
      delBtn.textContent = "Удалить";
      delBtn.className = "danger";
      delBtn.onclick = () => deleteHistory(id);

      td2.appendChild(viewBtn);
      td2.appendChild(document.createTextNode(" "));
      td2.appendChild(delBtn);

      tr.appendChild(td1);
      tr.appendChild(td2);
      listEl.appendChild(tr);
    }
  } catch (e) {
    setStatus(`Ошибка: ${e.message}`);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function loadHistory(id) {
  messagesEl.innerHTML = '<div class="chat-loading">Загрузка...</div>';
  try {
    const data = await api(`/admin/chat-histories/${encodeURIComponent(id)}?last_n=50`);
    
    if (!data.messages || data.messages.length === 0) {
      messagesEl.innerHTML = '<div class="chat-empty">Нет сообщений</div>';
      tidEl.value = id;
      return;
    }
    
    let html = '<div class="chat-messages">';
    for (const msg of data.messages) {
      if (msg.role === 'user') {
        html += `
          <div class="message user">
            <div class="role">👤 Пользователь</div>
            <div class="content">${escapeHtml(msg.content)}</div>
          </div>
        `;
      } else if (msg.role === 'assistant') {
        html += `
          <div class="message assistant">
            <div class="role">🤖 Ассистент</div>
            <div class="content">${escapeHtml(msg.content)}</div>
          </div>
        `;
      }
    }
    html += '</div>';
    
    messagesEl.innerHTML = html;
    tidEl.value = id;
  } catch (e) {
    messagesEl.innerHTML = `<div class="chat-error">Ошибка: ${escapeHtml(e.message)}</div>`;
  }
}

async function deleteHistory(id) {
  if (!confirm(`Удалить историю для ${id}?`)) return;
  try {
    await api(`/admin/chat-histories/${encodeURIComponent(id)}`, { method: "DELETE" });
    await refresh();
    if (tidEl.value === id) messagesEl.innerHTML = '<div class="chat-empty">(пусто)</div>';
  } catch (e) {
    alert(`Ошибка: ${e.message}`);
  }
}

async function deleteAll() {
  if (!confirm("Удалить ВСЕ истории?")) return;
  try {
    const data = await api("/admin/chat-histories", { method: "DELETE" });
    alert(`Удалено ключей: ${data.deleted}`);
    await refresh();
    messagesEl.innerHTML = '<div class="chat-empty">(пусто)</div>';
  } catch (e) {
    alert(`Ошибка: ${e.message}`);
  }
}

document.getElementById("refresh").onclick = refresh;
document.getElementById("deleteAll").onclick = deleteAll;
document.getElementById("loadOne").onclick = () => {
  const id = (tidEl.value || "").trim();
  if (id) loadHistory(id);
};
document.getElementById("deleteOne").onclick = () => {
  const id = (tidEl.value || "").trim();
  if (id) deleteHistory(id);
};

refresh();