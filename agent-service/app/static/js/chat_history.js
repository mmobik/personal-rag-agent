const statusEl = document.getElementById("status");
const listEl = document.getElementById("list");
const tidEl = document.getElementById("tid");
const messagesEl = document.getElementById("messages");

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
    // Добавляем Basic Auth заголовок
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData && userData.email && userData.api_key) {
      const credentials = btoa(`${userData.email}:${userData.api_key}`);
      opts.headers = {
        ...opts.headers,
        'Authorization': `Basic ${credentials}`
      };
    }

    const res = await fetch(path, opts);
    
    // Проверяем тип контента
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
    const data = await api("/api/v1/admin/chat-histories");
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

async function loadHistory(id) {
  messagesEl.textContent = "(загрузка...)";
  try {
    const data = await api(`/api/v1/admin/chat-histories/${encodeURIComponent(id)}?last_n=50`);
    messagesEl.textContent = JSON.stringify(data.messages, null, 2);
    tidEl.value = id;
  } catch (e) {
    messagesEl.textContent = `Ошибка: ${e.message}`;
  }
}

async function deleteHistory(id) {
  if (!confirm(`Удалить историю для ${id}?`)) return;
  try {
    await api(`/api/v1/admin/chat-histories/${encodeURIComponent(id)}`, { method: "DELETE" });
    await refresh();
    if (tidEl.value === id) messagesEl.textContent = "(пусто)";
  } catch (e) {
    alert(`Ошибка: ${e.message}`);
  }
}

async function deleteAll() {
  if (!confirm("Удалить ВСЕ истории?")) return;
  try {
    const data = await api("/api/v1/admin/chat-histories", { method: "DELETE" });
    alert(`Удалено ключей: ${data.deleted}`);
    await refresh();
    messagesEl.textContent = "(пусто)";
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
