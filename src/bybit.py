# Исправленная версия bybit.py с поддержкой API v5

import os
import json
import requests
import time
import hashlib
import hmac
from pprint import pprint

api_key = ''
secret_key = ''
url = "https://api.bybit.com"
recv_window = "5000"

def find_config():
    """Ищет config.json в различных возможных расположениях"""
    possible_paths = [
        "config.json",
        "src/config.json", 
        "../config.json",
        "../src/config.json"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Найден config.json по пути: {path}")
            return path
    
    raise FileNotFoundError("Файл config.json не найден ни в одном из ожидаемых мест")

def get_info_from_json():
    global api_key, secret_key
    
    config_path = find_config()
    
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        if 'API_KEY_BYBIT' not in data or 'API_SECRET_KEY_BYBIT' not in data:
            raise KeyError("В config.json отсутствуют необходимые ключи")
            
        api_key = data['API_KEY_BYBIT']
        secret_key = data['API_SECRET_KEY_BYBIT']
        
        if not api_key or not secret_key:
            raise ValueError("API-ключи не могут быть пустыми.")
            
        print("Конфигурация Bybit загружена успешно!")
        
    except json.JSONDecodeError:
        raise ValueError("Ошибка чтения JSON")

def get_sign_for_get(params_str, time_stamp):
    param_str = f"{time_stamp}{api_key}{recv_window}{params_str}"
    hash_obj = hmac.new(secret_key.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    return hash_obj.hexdigest()

def get_sign_for_post(payload_str, timestamp):
    message = f"{timestamp}{api_key}{recv_window}{payload_str}"
    signature = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def send_request(endpoint, method, params_dict=None):
    signature = ''
    time_stamp = str(int(time.time() * 1000))
    
    if params_dict:
        params_str = "&".join([f"{k}={v}" for k, v in sorted(params_dict.items())])
    else:
        params_str = ""
    
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2', 
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    url_full = url + endpoint
    
    try:
        if method == "POST":
            payload = json.dumps(params_dict, separators=(',', ':'))
            signature = get_sign_for_post(payload, time_stamp)
            headers['X-BAPI-SIGN'] = signature
            response = requests.request(method, url_full, headers=headers, data=payload)
        else:
            signature = get_sign_for_get(params_str, time_stamp)
            headers['X-BAPI-SIGN'] = signature  
            response = requests.request(method, url_full, headers=headers, params=params_dict)
        
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"[Ошибка сети] {e}")
        return {"error": "network", "message": str(e)}
    
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("[Ошибка] Не удалось декодировать JSON.")
        return {
            "error": "invalid_json", 
            "status_code": response.status_code,
            "text": response.text
        }

def get_balance():
    """
    Получает баланс аккаунта Bybit
    
    Returns:
        tuple: (общий_баланс_USDT, словарь_монет)
    """
    endpoint = '/v5/account/wallet-balance'
    params = {"accountType": "UNIFIED"}
    
    try:
        response = send_request(endpoint, "GET", params)
        
        if response.get("retCode") == 0 and response.get("result") and response["result"].get("list"):
            account_data = response['result']['list'][0]
            total_equity = float(account_data['totalEquity'])
            
            coins = {}
            for coin in account_data['coin']:
                equity = float(coin['equity'])
                if equity > 0:
                    coins[coin['coin']] = equity
            
            return total_equity, coins
        else:
            error_msg = response.get("retMsg", "Неизвестная ошибка")
            raise Exception(f"Ошибка API Bybit: {error_msg}")
            
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return 0.0, {}

def get_available_trading_pairs(amount_of_pair=1000):
    """
    Получает список доступных торговых пар
    
    Args:
        amount_of_pair (int): Максимальное количество пар для возврата
        
    Returns:
        list: Список торговых пар
    """
    endpoint = '/v5/market/instruments-info'
    params = {'category': 'spot'}
    
    try:
        response = send_request(endpoint, "GET", params)
        
        if response.get("retCode") == 0 and response.get("result") and response["result"].get("list"):
            trading_pairs = [pair['symbol'] for pair in response['result']['list']]
            
            if amount_of_pair > len(trading_pairs) or amount_of_pair < 0:
                return trading_pairs
            else:
                return trading_pairs[:amount_of_pair]
        else:
            error_msg = response.get("retMsg", "Неизвестная ошибка")
            print(f"Ошибка получения торговых пар: {error_msg}")
            return []
            
    except Exception as e:
        print(f"Ошибка получения торговых пар: {e}")
        return []

def get_opened_positions(settleCoin="USDT"):
    """
    Получает открытые позиции для указанной расчетной валюты
    
    Args:
        settleCoin (str): Расчетная валюта ("USDT" или "USDC")
        
    Returns:
        list: Список позиций [[symbol, avg_price, position_size], ...]
    """
    endpoint = "/v5/position/list"
    params = {
        "category": "linear",
        "settleCoin": settleCoin
    }
    
    try:
        response = send_request(endpoint, "GET", params)
        
        if response.get("retCode") == 0 and response.get("result") and response["result"].get("list"):
            result = []
            for position in response["result"]["list"]:
                symbol = position.get("symbol")
                avg_price = position.get("avgPrice", "0")
                position_size = position.get("size", "0")
                
                if symbol and float(position_size) > 0:
                    result.append([symbol, avg_price, position_size])
            
            return result
        else:
            error_msg = response.get("retMsg", "Неизвестная ошибка")
            raise Exception(f"Ошибка API Bybit: {error_msg}")
            
    except Exception as e:
        print(f"Ошибка получения позиций: {e}")
        return []

def convert_interval(interval):
    """Конвертирует интервал в формат Bybit"""
    map_bybit = {
        "1m": "1",
        "3m": "3", 
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "1h": "60",
        "2h": "120",
        "4h": "240",
        "6h": "360",
        "12h": "720",
        "1d": "D",
        "1w": "W",
        "1M": "M"
    }
    
    return map_bybit.get(interval, "15")

def get_some_last_kandle(symbol="BTCUSDT", interval="15m", limit=15):
    """
    Получает последние свечи для торговой пары
    
    Args:
        symbol (str): Торговая пара
        interval (str): Интервал свечи
        limit (int): Количество свечей
        
    Returns:
        list: Список кортежей (open_price, close_price)
    """
    converted_interval = convert_interval(interval)
    
    available_kline_interval = ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"]
    
    if converted_interval not in available_kline_interval:
        print(f"Интервал {interval} не поддерживается. Используется 15m")
        converted_interval = "15"
    
    if limit <= 0:
        print("Количество свечей не может быть меньше 1. Используется 15")
        limit = 15
    
    endpoint = "/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": converted_interval,
        "limit": limit
    }
    
    try:
        response = send_request(endpoint, "GET", params)
        
        if response.get("retCode") == 0 and response.get("result") and response["result"].get("list"):
            list_of_candles = []
            for candle in response['result']['list']:
                list_of_candles.append((candle[1], candle[4]))
            
            return list_of_candles
        else:
            error_msg = response.get("retMsg", "Неизвестная ошибка")
            print(f"Ошибка получения свечей: {error_msg}")
            return []
            
    except Exception as e:
        print(f"Ошибка получения свечей: {e}")
        return []

def place_order(side, amount, symbol):
    """
    Размещает рыночный ордер
    
    Args:
        side (str): "Buy" или "Sell"
        amount (float): Сумма в USDT
        symbol (str): Торговая пара
        
    Returns:
        str: Результат операции
    """
    if side not in ("Buy", "Sell"):
        return 'Параметр side должен быть "Buy" или "Sell"'
    
    if amount <= 0:
        return 'Сумма должна быть больше нуля'
    
    available_pairs = get_available_trading_pairs()
    if symbol not in available_pairs:
        return f'Торговая пара {symbol} не найдена'
    
    endpoint = "/v5/order/create"
    params = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(amount),
        "marketUnit": "quoteCoin"
    }
    
    try:
        response = send_request(endpoint, "POST", params)
        
        if response.get("retCode") == 0:
            return "OK"
        else:
            error_msg = response.get("retMsg", "Неизвестная ошибка")
            return f"Ошибка: {error_msg}"
            
    except Exception as e:
        return f"Ошибка размещения ордера: {e}"

if __name__ == "__main__":
    # Тест функций
    try:
        get_info_from_json()
        print("Подключение к Bybit настроено")
        
        # Тест баланса
        total, coins = get_balance()
        print(f"Баланс: {total} USDT, Монеты: {coins}")
        
        # Тест позиций
        positions = get_opened_positions()
        print(f"Позиции: {positions}")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")