import pandas as pd


def generate_breakout_signal(df: pd.DataFrame, params: dict) -> str:
    
    window_sr = params.get("window_sr", 5)
    df['support'] = df['low'].rolling(window=window_sr).min()
    df['resistance'] = df['high'].rolling(window=window_sr).min()

    latest = df.iloc[-1]
    price = latest['close']

    threshold = params.get("threshold_percent", 0.01)

    if price > latest['resistance'] * (1 + threshold):
        return 'buy'
    elif price < latest['support'] * (1 - threshold):
        return 'sell'
    else:
        return 'hold'