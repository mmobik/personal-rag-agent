# personal-rag-agent

Проект для создания цифрового двойника. Микросервисная архитектура: Telegram-бот, API Gateway, Agent Service (PostgreSQL, Redis), RAG Service (Qdrant). Лицензия: GPL-3.0 (см. [LICENSE](LICENSE)). Использование, распространение и модификация — в соответствии с условиями лицензии.

## Стек

- **Клиент:** Telegram Bot (aiogram)
- **Шлюз:** API Gateway (FastAPI)
- **Бизнес-логика:** Agent Service (FastAPI, PostgreSQL, Redis)
- **Векторный поиск:** RAG Service (FastAPI, Qdrant)
- **Оркестрация:** Docker Compose

## Запуск

```bash
docker compose up -d --build
```

Переменные окружения задаются в `.env` каждого сервиса (см. `telegram-bot/.env`, `agent-service/.env`, `api-gateway/.env`, `rag-service/.env`).

## Дальнейшие шаги

1. Обучение специализированных адаптеров на основе чатов Telegram
2. Взаимодействие с Redis (очереди, кэш, состояние)
3. Интеграция с LLM: планируется DeepSeek API
4. Векторная база: Qdrant — индексация и поиск по эмбеддингам

## Структура репозитория

```
agent-service/   — агенты, пользователи, PostgreSQL, Redis
api-gateway/     — маршрутизация запросов
rag-service/     — RAG, Qdrant
telegram-bot/    — клиент Telegram
backups/         — дампы БД (скрипты в scripts/)
scripts/         — backup/restore (PowerShell и Bash)
```
