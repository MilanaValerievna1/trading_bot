import pandas as pd
import os


def load_order_book_from_csv(symbol='BTCUSDT', file_path=None):
    if file_path is None:
        file_path = f"data/{symbol}_orderbook.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден")

    df = pd.read_csv(file_path)

    bids = df[df['type'] == 'bid'][['price', 'quantity']]
    asks = df[df['type'] == 'ask'][['price', 'quantity']]

    return {
        'bids': bids.values.tolist(),
        'asks': asks.values.tolist()
    }


def get_best_bid(order_book):

    if order_book['bids']:
        return max(order_book['bids'], key=lambda x: x[0])[0]
    return None


def get_best_ask(order_book):

    if order_book['asks']:
        return min(order_book['asks'], key=lambda x: x[0])[0]
    return None


def check_liquidity(order_book, threshold=2):

    total_bid_volume = sum(qty for _, qty, _ in order_book['bids'])
    total_ask_volume = sum(qty for _, qty, _ in order_book['asks'])

    return total_bid_volume >= threshold and total_ask_volume >= threshold