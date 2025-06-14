from cryptography.fernet import Fernet
import os

KEY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
KEY_PATH = os.path.join(KEY_DIR, 'secret.key')

def generate_key():
    return Fernet.generate_key()

def save_key(key, key_file=KEY_PATH):
    os.makedirs(KEY_DIR, exist_ok=True)
    with open(key_file, 'wb') as f:
        f.write(key)

def load_key(key_file=KEY_PATH):
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Ключ не найден по пути: {key_file}")
    with open(key_file, 'rb') as f:
        return f.read()

def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

key = generate_key()
save_key(key)
encrypted_api_key = encrypt_data("YOUR_API_KEY", key)