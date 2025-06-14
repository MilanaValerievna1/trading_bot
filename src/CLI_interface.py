from .bybit import get_balance as bybit_balance, get_available_trading_pairs as bybit_pairs, \
                 get_opened_positions as bybit_positions, get_some_last_kandle as bybit_kline, \
                 place_order as bybit_order, get_info_from_json as get_info_bybit

from .okx import get_balance as okx_balance, get_available_trading_pairs as okx_pairs, \
               get_opened_positions as okx_positions, get_some_last_kandle as okx_kline, \
               place_order as okx_order, get_info_from_json as get_info_okx

from .server import start_server

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def print_welcome():
    print("\n" + "="*50)
    print("=== Терминальный интерфейс управления биржевыми аккаунтами ===")
    print("="*50 + "\n")
    print("Веб-сервер запущен и доступен по адресу: http://localhost:5000\n")

    get_info_bybit()
    get_info_okx()


def handle_command(command):
    parts = command.split()
    if not parts:
        return True
    
    cmd = parts[0].lower()
    
    if cmd == "/balance":
        print("\nТекущий баланс:")
        
        b_total, b_coins = bybit_balance()
        print(f"Bybit: {b_total} USDT | Монеты: {b_coins}")
        
        o_total, o_coins = okx_balance()
        print(f"OKX: {o_total} USDT | Монеты: {o_coins}")
    
    elif cmd == "/pairs":
        print("\nДоступные пары:")
        print("Bybit:", bybit_pairs(3))
        print("OKX:", okx_pairs(3))
    
    elif cmd == "/positions":
        print("\nОткрытые позиции:")
        print("Bybit:", bybit_positions())
        print("OKX:", okx_positions())
    
    elif cmd == "/chart":
        if len(parts) >= 3:
            exchange = parts[1].lower()
            pair = parts[2]
            if exchange == "bybit":
                data = bybit_kline(symbol=pair)
                plot_chart(data, f"Bybit {pair}")
            elif exchange == "okx":
                data = okx_kline(symbol=pair)
                plot_chart(data, f"OKX {pair}")
            else:
                print("Неизвестная биржа. Используйте bybit или okx")
        else:
            print("\nИспользуйте: /chart [bybit|okx] [пара]")
    
    elif cmd in ("/buy", "/sell") and len(parts) >= 4:
        exchange = parts[1].lower()
        pair = parts[2]
        amount = parts[3]
        try:
            amount = float(amount)
            if exchange == "bybit":
                result = bybit_order("Buy" if cmd == "/buy" else "Sell", amount, pair)
                print(f"Результат: {result}")
            elif exchange == "okx":
                result = okx_order("buy" if cmd == "/buy" else "sell", amount, pair)
                print(f"Результат: {result}")
            else:
                print("Неизвестная биржа. Используйте bybit или okx")
        except ValueError:
            print("Неверная сумма. Введите число.")
    
    elif cmd == "/help":
        print_help()
    
    elif cmd == "/exit":
        return False
    
    else:
        print("\nНеизвестная команда. Введите /help")
    
    return True

def plot_chart(data, title):
    """Рисует график цен"""
    if not data:
        print("Нет данных для построения графика")
        return
    
    try:
        prices = [float(close) for _, close in data]
        indices = range(len(prices))
        
        plt.figure(figsize=(10, 5))
        plt.plot(indices, prices, marker='o', linestyle='-')
        plt.title(title)
        plt.xlabel('Период')
        plt.ylabel('Цена')
        plt.grid(True)
        plt.show()
    except Exception as e:
        print(f"Ошибка при построении графика: {e}")


def print_help():
    print("\nДоступные команды:")
    print("/balance - показать баланс")
    print("/pairs - список торговых пар")
    print("/positions - открытые позиции")
    print("/chart [bybit|okx] [пара] - график цен")
    print("/buy [bybit|okx] [пара] [сумма] - купить")
    print("/sell [bybit|okx] [пара] [сумма] - продать")
    print("/help - справка")
    print("/exit - выход")
    print("\nВеб-интерфейс доступен по адресу: http://localhost:5000\n")

def main():
    
    start_server()
    
    print_welcome()
    print_help()

    while True:
        try:
            command = input(">>> Введите команду: ").strip()
            if not handle_command(command):
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            sys.exit(0)
        except Exception as e:
            print(f"\nОшибка: {e}")

if __name__ == "__main__":
    main()
