def generate_arbitrage_signal(price_a, price_b, min_spread=0.005):
    if price_a <= 0 or price_b <= 0:
        raise ValueError("Цены должны быть положительными")

    spread_abs = abs(price_b - price_a)
    average_price = (price_a + price_b) / 2
    spread_percent = spread_abs / average_price

    if spread_percent < min_spread:
        return 'hold'

    if price_a < price_b:
        return f'buy_bybit_sell_okx_{spread_percent:.4f}'
    else:
        return f'buy_okx_sell_bybit_{spread_percent:.4f}'