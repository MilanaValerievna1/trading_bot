def get_strategy(strategy_name):

    strategies = {
        'dynamic_scalping': generate_dynamic_scalping_signal,
        'breakout': generate_breakout_signal,
        'ema_crossover': generate_ema_crossover_signal,
        'arbitrage': generate_arbitrage_signal
    }
    return strategies.get(strategy_name.lower())