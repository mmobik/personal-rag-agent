Dev mode — быстрое локальное развитие

Простая команда для запуска сервиса в режиме разработки (bind-mounts + hot reload):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

Остановить:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Файлы для правки в dev-режиме:
- `agent-service/app/templates`
- `agent-service/app/static`
- Код Python (`agent-service/app/...`) — при изменениях `uvicorn --reload` перезапустит процесс автоматически.
