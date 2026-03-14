"""
Скрипт для инициализации базы данных
Создаёт все таблицы на основе моделей
"""
from app.db import engine, Base

def init_db():
    """Создать все таблицы"""
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
