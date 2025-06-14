import os
import json
from datetime import datetime

import requests
import hashlib
import base64
import hmac
from pprint import pprint


api_key = ''
secret_key = ''
api_passphrase = ''
url = "https://www.okx.com"


def get_info_from_json():
    global api_key, secret_key, api_passphrase

    if not os.path.exists("config.json"):
        raise FileNotFoundError("Файл config.json не найден.")

    try:
        with open("config.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if 'API_KEY_OKX' not in data or 'API_SECRET_KEY_OKX' not in data or 'API_PASSPHRASE' not in data:
            raise KeyError("В config.json отсутствуют необходимые ключи: "
                           "'API_KEY_OKX' или 'API_SECRET_KEY_OKX' или 'API_PASSPHRASE'")

        api_key = data['API_KEY_OKX']
        secret_key = data['API_SECRET_KEY_OKX']
        api_passphrase = data['API_PASSPHRASE']

        if not api_key or not secret_key or not api_passphrase:
            raise ValueError("API-ключи не могут быть пустыми.")

    except json.JSONDecodeError:
        raise ValueError("Ошибка чтения JSON. Проверьте формат config.json.")


def get_okx_timestamp() -> str:
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def get_sign(timestamp: str, method: str, request_path: str, params: dict, body: str = "") -> str:
    params_str = str()
    count = 0
    if params:
        params_str += "?"
        for key, value in params.items():
            params_str += key + "=" + value
            count += 1
            if count < len(params):
                params_str += "&"

    pre_hash_string = timestamp + method.upper() + request_path + params_str + body

    print("Подпись: ", pre_hash_string)

    signature = hmac.new(
        secret_key.encode('utf-8'),
        pre_hash_string.encode('utf-8'),
        hashlib.sha256
    ).digest()

    return base64.b64encode(signature).decode()


def send_request(endpoint: str, method: str, params: dict = None, body: dict = None):
    timestamp = get_okx_timestamp()
    body_str = json.dumps(body, separators=(',', ':')) if body else ""
    
    headers = {
        'OK-ACCESS-SIGN': get_sign(timestamp, method, endpoint, params, body_str),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
        'Content-Type': 'application/json'
    }

    url_full = url + endpoint

    try:
        if method == "POST":
            response = requests.post(url_full, headers=headers, data=body_str)
        else:
            response = requests.get(url_full, headers=headers, params=params)

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
    endpoint = '/api/v5/account/balance'
    params = {"accountType": "UNIFIED"}
    response = send_request(endpoint, "GET", params)
    total_equity = response['data'][0]['totalEq']

    coins = dict()
    coins_pars = response['data'][0]['details']
    for coin in coins_pars:
        coins[coin["ccy"]] = coin["eq"]

    return total_equity, coins


def get_available_trading_pairs(amount_of_pair=1000):
    endpoint = "/api/v5/public/instruments"
    params = {"instType": "SPOT"}
    response = send_request(endpoint, "GET", params)
    
    trading_pairs = [trading_pair["instId"] for trading_pair in response["data"]]
    
    if amount_of_pair > len(trading_pairs) or amount_of_pair < 0:
        return trading_pairs
    else:
        return trading_pairs[:amount_of_pair]


def get_opened_positions():
    endpoint = "/api/v5/account/positions"
    params = {}
    response = send_request(endpoint, "GET", params)

    result = list()
    if response["data"]:
        for position in response["data"]:
            traiding_pair = position["instId"]
            avg_px = position["avgPx"]
            pos = position["pos"]
            result.append([traiding_pair, avg_px, pos])
    return result

def convert_interval(interval):
    map_okx = {
        "15m": "15m",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    }

    return map_okx[interval]



def get_some_last_kandle(symbol="BTC-USDT", interval="15m", limit=15):
    """
    Получает последние свечи для указанной торговой пары.
    
    Параметры:
        symbol (str): Торговая пара (например, "BTC-USDT")
        interval (str): Интервал свечи (по умолчанию "15m" - 15 минут)
        limit (int): Количество свечей (по умолчанию 15)
    
    Возвращает:
        list: Список кортежей (open_price, close_price) для каждой свечи
    """
    available_intervals = ["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H",
                            "6H", "12H", "1D", "1W", "1M"]
    
    interval = convert_interval(interval)
    
    if interval not in available_intervals:
        print(f"Недопустимый интервал. Используется 15m. Доступные: {available_intervals}")
        interval = "15m"
    
    if limit <= 0:
        print("Количество свечей не может быть меньше 1. Используется 15.")
        limit = 15
    
    endpoint = "/api/v5/market/candles"
    params = {
        "instId": symbol,
        "bar": interval,
        "limit": str(limit)
    }
    
    response = send_request(endpoint, "GET", params)
    
    list_of_candles = []
    if response and 'data' in response:
        for candle in response['data']:
            list_of_candles.append((candle[1], candle[4]))
    
    return list_of_candles


def place_order(side, amount, symbol):
    """
    Размещает ордер на OKX.
    
    Параметры:
        side (str): "buy" или "sell"
        amount (float): Количество базовой валюты
        symbol (str): Торговая пара (например "BTC-USDT")
    
    Возвращает:
        str: Ответ от API OKX
    """
    if side.lower() not in ("buy", "sell"):
        print("Параметр side принимает значения только 'buy' или 'sell'")
        return 'Invalid side parameter'
    
    if amount <= 0:
        print("Количество не может быть меньше или равно нулю")
        return 'Invalid amount'
    
    endpoint = "/api/v5/trade/order"
    
    params = {
        "instId": symbol,
        "tdMode": "cash",
        "side": side.lower(),
        "ordType": "market",
        "sz": str(amount),
    }
    
    response = send_request(endpoint, "POST", body=params)
    
    if response and 'data' in response:
        return response['data'][0]['sMsg']
    else:
        return 'No response from API'


if __name__ == "__main__":
    get_info_from_json()
    print(get_balance())
    print(place_order("buy", 10, "BTC-USDT"))