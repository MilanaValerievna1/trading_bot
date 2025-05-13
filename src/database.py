import sqlite3
from sqlite3 import Error
import os

# Константы путей
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'trading_bot.db')

def create_connection():
    """Создает соединение с базой данных"""
    conn = None
    try:
        # Создаем папку database, если ее нет
        os.makedirs(DB_DIR, exist_ok=True)
        
        print(f"Подключаемся к БД по пути: {DB_PATH}")  # Для отладки
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
    return conn

def init_db():
    """Инициализирует структуру базы данных"""
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            exchange TEXT NOT NULL,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            volume REAL NOT NULL,
            status TEXT CHECK(status IN ('open', 'closed', 'canceled'))
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS risk_limits (
            daily_loss_limit REAL DEFAULT 5.0,
            max_open_trades INTEGER DEFAULT 10,
            slippage_tolerance REAL DEFAULT 0.5
        );
        '''
    ]
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(table)
            conn.commit()
            print("База данных успешно инициализирована")
        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()