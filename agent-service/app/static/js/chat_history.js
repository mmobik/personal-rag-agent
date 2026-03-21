const statusEl = document.getElementById("status");
const listEl = document.getElementById("list");
const tidEl = document.getElementById("tid");
const messagesEl = document.getElementById("messages");

function setStatus(text) {
  statusEl.textContent = text;
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {}
  if (!res.ok) {
    throw new Error((data && (data.detail || data.message)) || text || `HTTP ${res.status}`);
  }
  return data;
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
