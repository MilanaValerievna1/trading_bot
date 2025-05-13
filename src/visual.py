import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from src.database import DB_PATH

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')

def plot_profit():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql('''
            SELECT timestamp, price, volume, 
                   CASE WHEN side = 'buy' THEN -price*volume ELSE price*volume END as profit
            FROM trades WHERE status = 'closed'
        ''', conn)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df['cumulative'] = df['profit'].cumsum()
        
        plt.figure(figsize=(12, 6))
        df['cumulative'].plot(title='Кумулятивная прибыль', grid=True)
        plt.savefig(os.path.join(REPORTS_DIR, 'profit_chart.png'))
        plt.close()
    except Exception as e:
        print(f"Ошибка визуализации: {e}")
    finally:
        conn.close()