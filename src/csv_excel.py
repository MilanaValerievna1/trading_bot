import pandas as pd
import sqlite3
import os
from src.database import DB_PATH

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')

def generate_report():
    """Генерирует отчеты в CSV и Excel форматах"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        df_trades = pd.read_sql('SELECT * FROM trades', conn)
        
        csv_path = os.path.join(REPORTS_DIR, 'trades_report.csv')
        excel_path = os.path.join(REPORTS_DIR, 'trades_report.xlsx')
        
        df_trades.to_csv(csv_path, index=False, encoding='utf-8')
        df_trades.to_excel(excel_path, index=False)
        
        print(f"Отчеты сохранены в: {REPORTS_DIR}")
    except Exception as e:
        print(f"Ошибка генерации отчета: {e}")
    finally:
        conn.close()