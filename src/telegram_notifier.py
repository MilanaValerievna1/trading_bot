import requests

def send_telegram_alert(message, bot_token='YOUR_BOT_TOKEN', chat_id='YOUR_CHAT_ID'):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")