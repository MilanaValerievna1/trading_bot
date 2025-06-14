from flask import Flask, render_template, request, jsonify
import threading
import time
import os
from pathlib import Path

template_dir = os.path.abspath('templates')

if not os.path.exists(template_dir):
    os.makedirs(template_dir, exist_ok=True)
    print(f"Создана папка шаблонов: {template_dir}")

app = Flask(__name__, template_folder=template_dir)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

try:
    from .bybit import (
        get_balance as bybit_balance,
        get_opened_positions as bybit_positions,
        get_some_last_kandle as bybit_kline,
        place_order as bybit_order,
        get_available_trading_pairs as bybit_pairs,
        get_info_from_json as get_info_bybit
    )
    
    from .okx import (
        get_balance as okx_balance,
        get_opened_positions as okx_positions,
        get_some_last_kandle as okx_kline,
        place_order as okx_order,
        get_available_trading_pairs as okx_pairs,
        get_info_from_json as get_info_okx
    )
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    
    from bybit import (
        get_balance as bybit_balance,
        get_opened_positions as bybit_positions,
        get_some_last_kandle as bybit_kline,
        place_order as bybit_order,
        get_available_trading_pairs as bybit_pairs,
        get_info_from_json as get_info_bybit
    )
    
    from okx import (
        get_balance as okx_balance,
        get_opened_positions as okx_positions,
        get_some_last_kandle as okx_kline,
        place_order as okx_order,
        get_available_trading_pairs as okx_pairs,
        get_info_from_json as get_info_okx
    )

@app.route('/')
def index():
    """Главная страница веб-интерфейса"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Ошибка шаблона</title></head>
        <body>
            <h1>Ошибка загрузки веб-интерфейса</h1>
            <p><strong>Проблема:</strong> {str(e)}</p>
            <p><strong>Решение:</strong></p>
            <ol>
                <li>Создайте папку <code>templates</code> в корне проекта</li>
                <li>Поместите файл <code>index.html</code> в папку <code>templates/</code></li>
                <li>Перезапустите сервер</li>
            </ol>
            <p><strong>CLI интерфейс работает нормально!</strong></p>
            <hr>
            <pre>Текущий путь шаблонов: {template_dir}</pre>
        </body>
        </html>
        """

@app.route('/balance')
def balance():
    """API для получения баланса с обеих бирж"""
    try:
        get_info_bybit()
        get_info_okx()
        
        bybit_total, bybit_coins = bybit_balance()
        okx_total, okx_coins = okx_balance()
        
        return jsonify({
            'bybit': {
                'total': bybit_total,
                'coins': bybit_coins,
                'positions': bybit_positions()
            },
            'okx': {
                'total': okx_total,
                'coins': okx_coins,
                'positions': okx_positions()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart')
def chart():
    """API для получения данных графика"""
    try:
        exchange = request.args.get('exchange', 'bybit')
        pair = request.args.get('pair', 'BTCUSDT')
        interval = request.args.get('interval', '15m')
        
        if exchange == 'bybit':
            data = bybit_kline(symbol=pair, interval=interval)
        else:
            data = okx_kline(symbol=pair, interval=interval)
        
        return jsonify({
            'labels': [str(i) for i in range(len(data))],
            'open': [float(x[0]) for x in data],
            'close': [float(x[1]) for x in data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trade', methods=['POST'])
def trade():
    """API для размещения ордеров"""
    try:
        data = request.json
        exchange = data['exchange']
        pair = data['pair']
        side = data['side']
        amount = float(data['amount'])
        
        if exchange == 'bybit':
            bybit_side = "Buy" if side.lower() == "buy" else "Sell"
            result = bybit_order(bybit_side, amount, pair)
        else:
            okx_side = side.lower()
            result = okx_order(okx_side, amount, pair)
        
        if isinstance(result, dict):
            message = result.get('retMsg') or result.get('sMsg') or result.get('msg')
            if message and message.upper() == 'OK':
                return jsonify({'result': 'OK'})
            elif message:
                return jsonify({'result': message})
            else:
                return jsonify({'result': 'Успешно'})
        else:
            return jsonify({'result': result or 'OK'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/pairs')
def pairs():
    """API для получения списка торговых пар"""
    try:
        exchange = request.args.get('exchange', 'bybit')
        limit = int(request.args.get('limit', 10))
        
        if exchange == 'bybit':
            return jsonify(bybit_pairs(limit))
        else:
            return jsonify(okx_pairs(limit))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Обработчик 404 ошибок"""
    return jsonify({'error': 'Страница не найдена'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500 ошибок"""
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

def run_server():
    """Запуск Flask сервера"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")

def start_server():
    """Запуск сервера в отдельном потоке"""
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    print("Сервер запущен на http://localhost:5000")

if __name__ == '__main__':
    start_server()
    print("Веб-сервер работает...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановка сервера...")