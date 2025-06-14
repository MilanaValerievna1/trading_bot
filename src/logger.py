import logging
from datetime import datetime
from src.database import create_connection, DB_PATH
import os
from sqlite3 import Error
import sqlite3

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

class BotLogger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.conn = create_connection()
        
        logging.basicConfig(
            filename=os.path.join(LOG_DIR, 'bot_activity.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8',
            filemode='a'
        )
        self.logger = logging.getLogger('bot_logger')
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        if hasattr(console_handler.stream, 'reconfigure'):
            console_handler.stream.reconfigure(encoding='utf-8')
        
        self.logger.addHandler(console_handler)

    def log_event(self, event_type, details):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO logs (timestamp, event_type, details) VALUES (?, ?, ?)",
                (timestamp, event_type, str(details)))
            self.conn.commit()
            self.logger.info(f"{event_type}: {details}")
        except sqlite3.Error as e:
            self.logger.error(f"DB Error: {str(e)}")
            self.conn.rollback()
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()