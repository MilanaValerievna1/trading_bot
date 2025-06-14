"""
Торговые стратегии
"""

from .arbitrage_strategy import generate_arbitrage_signal
from .breakout_strategy import generate_breakout_signal
from .dynamic_scalping_strategy import generate_signal as generate_scalping_signal
from .ema_crossover_strategy import generate_ema_signal
from .base_strategy import generate_signal_template

__all__ = [
    'generate_arbitrage_signal',
    'generate_breakout_signal', 
    'generate_scalping_signal',
    'generate_ema_signal',
    'generate_signal_template'
]

STRATEGIES = {
    'arbitrage': generate_arbitrage_signal,
    'breakout': generate_breakout_signal,
    'scalping': generate_scalping_signal,
    'ema_crossover': generate_ema_signal
}

def get_strategy(name):
    """Получает стратегию по имени."""
    return STRATEGIES.get(name.lower())

def list_strategies():
    """Возвращает список доступных стратегий."""
    return list(STRATEGIES.keys())