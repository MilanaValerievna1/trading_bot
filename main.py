import sys
import os
from pathlib import Path
from src.database import init_db, DB_PATH
from src.logger import BotLogger

sys.path.append("C:\Учеба\Питон\trading_bot")

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    # Инициализация БД
    print(f"Инициализация базы данных по пути: {DB_PATH}")
    init_db()
    
    # Проверка создания файла БД
    if os.path.exists(DB_PATH):
        print("✅ База данных успешно создана")
    else:
        print("❌ Ошибка: база данных не создана")
    
    # Тестирование логгера
    logger = BotLogger()
    logger.log_event("TEST", "Проверка работы логгера")

if __name__ == "__main__":
    main()