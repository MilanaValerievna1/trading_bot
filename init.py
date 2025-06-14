"""
Торговый бот для криптовалют
Поддерживает биржи Bybit и OKX
"""

__version__ = "1.0.0"
__author__ = "Trading Bot Team"

from .src import database, logger

__all__ = ['database', 'logger']