import sqlite3
from sqlite3 import Error
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'trading_bot.db')

def create_connection():
    """Создает соединение с базой данных"""
    conn = None
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        print(f"Подключаемся к БД по пути: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

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
            id INTEGER PRIMARY KEY,
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
            return True
        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False
        finally:
            conn.close()
    else:
        return False

def check_database_health():
    """Проверяет состояние базы данных"""
    try:
        conn = create_connection()
        if not conn:
            return {
                "status": "error",
                "message": "Не удалось подключиться к базе данных",
                "tables_exist": False,
                "connection_ok": False
            }
        
        cursor = conn.cursor()
        
        tables_to_check = ['logs', 'trades', 'risk_limits']
        existing_tables = []
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if cursor.fetchone():
                existing_tables.append(table)
        
        tables_exist = len(existing_tables) == len(tables_to_check)
        
        conn.close()
        
        return {
            "status": "ok" if tables_exist else "warning",
            "message": "База данных работает корректно" if tables_exist else "Некоторые таблицы отсутствуют",
            "tables_exist": tables_exist,
            "existing_tables": existing_tables,
            "connection_ok": True
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Ошибка проверки БД: {str(e)}",
            "tables_exist": False,
            "connection_ok": False
        }

def get_db_stats():
    """Возвращает статистику базы данных"""
    try:
        conn = create_connection()
        if not conn:
            return {
                "error": "Не удалось подключиться к базе данных",
                "logs_count": 0,
                "trades_count": 0,
                "risk_limits_set": False
            }
        
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM logs")
        logs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades")  
        trades_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM risk_limits")
        risk_limits_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "logs_count": logs_count,
            "trades_count": trades_count,
            "risk_limits_set": risk_limits_count > 0,
            "database_size": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        }
        
    except Exception as e:
        return {
            "error": f"Ошибка получения статистики: {str(e)}",
            "logs_count": 0,
            "trades_count": 0,
            "risk_limits_set": False
        }

if __name__ == "__main__":
    init_db()