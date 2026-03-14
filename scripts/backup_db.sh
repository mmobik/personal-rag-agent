#!/bin/bash
# Скрипт для создания backup PostgreSQL

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/agent_db_$TIMESTAMP.sql"

echo "Создание backup базы данных..."
docker exec agent-postgres pg_dump -U postgres agent_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup успешно создан: $BACKUP_FILE"
    
    # Удаляем старые бэкапы (старше 7 дней)
    find "$BACKUP_DIR" -name "agent_db_*.sql" -type f -mtime +7 -delete
    echo "🗑️  Старые бэкапы удалены"
else
    echo "❌ Ошибка при создании backup"
    exit 1
fi
