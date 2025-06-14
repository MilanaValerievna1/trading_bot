import pandas as pd
import time
from .strategies.dynamic_scalping_strategy import generate_signal as scalping_signal
from src.strategies.breakout_strategy import generate_breakout_signal
from src.strategies.ema_crossover_strategy import generate_ema_signal


def simulate_realtime_data(file_path='data/BTCUSDT_1m.csv', window=50):
    df = pd.read_csv(file_path)

    for i in range(window, len(df), 5):
        yield df.iloc[i - window:i].reset_index(drop=True)
        time.sleep(1)


def run_realtime_trading(strategy_func, params=None):
    print("Движок запущен в режиме реального времени (упрощённая версия)")
    for df_window in simulate_realtime_data():
        try:
            signal = strategy_func(df_window, params or {})
            print(f"{time.ctime()} | Сигнал: {signal.upper()}")
        except Exception as e:
            print(f"Ошибка при генерации сигнала: {e}")

    print("Реальный режим завершён")


if __name__ == "__main__":
    strategy_params = {
        "sma_window": 20,
        "rsi_window": 14,
        "acceleration_threshold": 0.5,
        "take_profit_threshold": 1.0,
        "cut_loss_threshold": 1.0,
        "quantity_multiply": 1.5,
        "sma_gap": 0.01,
        "rsi_threshold": 10
    }

    print("Выберите стратегию:")
    print("1. Динамический скальпинг")
    print("2. Пробой уровней")
    print("3. EMA Crossover")

    choice = input("Введите номер стратегии (1, 2 или 3): ").strip()

    if choice == '1':
        strategy_function = scalping_signal
    elif choice == '2':
        strategy_function = generate_breakout_signal
    elif choice == '3':
        strategy_function = generate_ema_signal
    else:
        print("Неверный выбор")
        exit()

    run_realtime_trading(strategy_function, strategy_params)