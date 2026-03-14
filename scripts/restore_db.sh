#!/bin/bash
# Скрипт для восстановления базы данных из backup

if [ -z "$1" ]; then
    echo "Использование: ./restore_db.sh <путь_к_backup_файлу>"
    echo "Пример: ./restore_db.sh ./backups/agent_db_20260313_220000.sql"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Файл не найден: $BACKUP_FILE"
    exit 1
fi

echo "Восстановление базы данных из $BACKUP_FILE..."
cat "$BACKUP_FILE" | docker exec -i agent-postgres psql -U postgres -d agent_db

if [ $? -eq 0 ]; then
    echo "✅ База данных успешно восстановлена!"
else
    echo "❌ Ошибка при восстановлении базы данных"
    exit 1
fi
