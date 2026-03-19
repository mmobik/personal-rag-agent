from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/ui/chat-history", response_class=HTMLResponse)
def chat_history_ui():
    # Минимальный UI без шаблонов, чистый HTML + fetch.
    return HTMLResponse(
        """
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Agent Service — Redis chat history</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 20px; }
      .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
      input { padding: 8px 10px; min-width: 320px; }
      button { padding: 8px 10px; cursor: pointer; }
      pre { background: #0b0f19; color: #e6edf3; padding: 12px; border-radius: 8px; overflow: auto; }
      table { border-collapse: collapse; width: 100%; margin-top: 12px; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
      th { background: #f5f5f5; }
      .muted { color: #666; }
    </style>
  </head>
  <body>
    <h2>Redis: chat history</h2>
    <p class="muted">Просмотр/удаление ключей <code>chat:history:*</code>. Не предназначено для публичного доступа.</p>

    <div class="row">
      <button id="refresh">Обновить список</button>
      <button id="deleteAll">Удалить все истории</button>
      <span id="status" class="muted"></span>
    </div>

    <h3>Поиск по telegram_id</h3>
    <div class="row">
      <input id="tid" placeholder="telegram_id (например 123456789)" />
      <button id="loadOne">Показать</button>
      <button id="deleteOne">Удалить</button>
    </div>

    <h3>Список</h3>
    <table>
      <thead>
        <tr>
          <th>telegram_id</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody id="list"></tbody>
    </table>

    <h3>Сообщения</h3>
    <pre id="messages">(пусто)</pre>

    <script>
      const statusEl = document.getElementById('status');
      const listEl = document.getElementById('list');
      const tidEl = document.getElementById('tid');
      const messagesEl = document.getElementById('messages');

      function setStatus(s) { statusEl.textContent = s; }

      async function api(path, opts) {
        const res = await fetch(path, opts);
        const text = await res.text();
        let data = null;
        try { data = text ? JSON.parse(text) : null; } catch {}
        if (!res.ok) {
          throw new Error((data && (data.detail || data.message)) || text || ('HTTP ' + res.status));
        }
        return data;
      }

      async function refresh() {
        setStatus('Загрузка...');
        listEl.innerHTML = '';
        try {
          const data = await api('/api/v1/admin/chat-histories');
          setStatus('Найдено: ' + data.count);
          for (const id of data.telegram_ids) {
            const tr = document.createElement('tr');
            const td1 = document.createElement('td');
            td1.textContent = id;
            const td2 = document.createElement('td');
            const b1 = document.createElement('button');
            b1.textContent = 'Показать';
            b1.onclick = () => loadHistory(id);
            const b2 = document.createElement('button');
            b2.textContent = 'Удалить';
            b2.onclick = () => deleteHistory(id);
            td2.appendChild(b1);
            td2.appendChild(document.createTextNode(' '));
            td2.appendChild(b2);
            tr.appendChild(td1);
            tr.appendChild(td2);
            listEl.appendChild(tr);
          }
        } catch (e) {
          setStatus('Ошибка: ' + e.message);
        }
      }

      async function loadHistory(id) {
        messagesEl.textContent = '(загрузка...)';
        try {
          const data = await api('/api/v1/admin/chat-histories/' + encodeURIComponent(id) + '?last_n=50');
          messagesEl.textContent = JSON.stringify(data.messages, null, 2);
          tidEl.value = id;
        } catch (e) {
          messagesEl.textContent = 'Ошибка: ' + e.message;
        }
      }

      async function deleteHistory(id) {
        if (!confirm('Удалить историю для ' + id + '?')) return;
        try {
          await api('/api/v1/admin/chat-histories/' + encodeURIComponent(id), { method: 'DELETE' });
          await refresh();
          if (tidEl.value === id) messagesEl.textContent = '(пусто)';
        } catch (e) {
          alert('Ошибка: ' + e.message);
        }
      }

      async function deleteAll() {
        if (!confirm('Удалить ВСЕ истории?')) return;
        try {
          const data = await api('/api/v1/admin/chat-histories', { method: 'DELETE' });
          alert('Удалено ключей: ' + data.deleted);
          await refresh();
          messagesEl.textContent = '(пусто)';
        } catch (e) {
          alert('Ошибка: ' + e.message);
        }
      }

      document.getElementById('refresh').onclick = refresh;
      document.getElementById('deleteAll').onclick = deleteAll;
      document.getElementById('loadOne').onclick = () => {
        const id = (tidEl.value || '').trim();
        if (id) loadHistory(id);
      };
      document.getElementById('deleteOne').onclick = () => {
        const id = (tidEl.value || '').trim();
        if (id) deleteHistory(id);
      };

      refresh();
    </script>
  </body>
</html>
        """.strip()
    )

