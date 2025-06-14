import pandas as pd


def generate_ema_signal(df: pd.DataFrame, params: dict) -> str:
    short_period = params.get("short_period", 5)
    long_period = params.get("long_period", 20)

    df['ema_short'] = df['close'].ewm(span=short_period, adjust=False).mean()
    df['ema_long'] = df['close'].ewm(span=long_period, adjust=False).mean()

    latest = df.iloc[-1]

    if latest['ema_short'] > latest['ema_long']:
        return 'buy'
    elif latest['ema_short'] < latest['ema_long']:
        return 'sell'
    else:
        return 'hold'