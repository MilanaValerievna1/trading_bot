import sqlite3
from src.database import DB_PATH
from src.telegram_notifier import send_telegram_alert

class RiskManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        
    def check_daily_loss(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT SUM((price * volume) * CASE WHEN side = 'sell' THEN 1 ELSE -1 END) 
                FROM trades 
                WHERE status = 'closed' AND date(timestamp) = date('now')
            ''')
            total_loss = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT daily_loss_limit FROM risk_limits')
            loss_limit = cursor.fetchone()[0]
            
            if total_loss <= -loss_limit:
                send_telegram_alert(f"Дневной лимит убытка достигнут: {-total_loss}")
                return False
            return True
        except sqlite3.Error as e:
            print(f"Ошибка RiskManager: {e}")
            return True