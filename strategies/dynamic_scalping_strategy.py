import pandas as pd
from src.indicators import calculate_atr, calculate_rsi, calculate_sma


def generate_signal(df: pd.DataFrame, params: dict) -> str:
    df = df.copy()

    df['ATR'] = calculate_atr(df, window=params.get('atr_window', 14))
    df['RSI'] = calculate_rsi(df, window=params.get('rsi_window', 14))
    df['SMA'] = calculate_sma(df, window=params.get('sma_window', 20))
    df['Price/SMA'] = df['close'] / df['SMA']
    df['Acceleration'] = df['close'] - df['close'].shift(1)
    df['Short Acceleration'] = df['close'] - df['close'].shift(1)
    df['Average Quantity'] = df['volume'].rolling(window=20).mean()

    latest = df.iloc[-1]

    long_conditions = [
        latest['Acceleration'] > params.get("acceleration_threshold", 0.5),
        latest['volume'] > latest['Average Quantity'] * params.get("quantity_multiply", 1.5),
        latest['Price/SMA'] < 1 - params.get("sma_gap", 0.01),
        latest['Short Acceleration'] > params.get("short_acceleration_threshold", 0.5),
        latest['RSI'] < 50 - params.get("rsi_threshold", 10)
    ]

    short_conditions = [
        latest['Acceleration'] < -params.get("acceleration_threshold", 0.5),
        latest['volume'] > latest['Average Quantity'] * params.get("quantity_multiply", 1.5),
        latest['Price/SMA'] > 1 + params.get("sma_gap", 0.01),
        latest['Short Acceleration'] < -params.get("short_acceleration_threshold", 0.5),
        latest['RSI'] > 50 + params.get("rsi_threshold", 10)
    ]

    if all(long_conditions):
        return 'buy'
    elif all(short_conditions):
        return 'sell'
    else:
        return 'hold'