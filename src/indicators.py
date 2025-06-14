import pandas as pd

def calculate_atr(data: pd.DataFrame, window=14) -> pd.Series:

    data = data.copy()
    data['H-L'] = data['high'] - data['low']
    data['H-PC'] = abs(data['high'] - data['close'].shift(1))
    data['L-PC'] = abs(data['low'] - data['close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    return data['TR'].rolling(window=window).mean()


def calculate_rsi(data: pd.DataFrame, window=14) -> pd.Series:

    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_sma(data: pd.DataFrame, window=20) -> pd.Series:

    return data['close'].rolling(window=window).mean()