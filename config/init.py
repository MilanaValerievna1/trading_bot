"""
Модуль конфигурации
"""

import os
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / 'config.json'

def load_config():
    """Загружает конфигурацию из config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config_data):
    """Сохраняет конфигурацию в config.json."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

__all__ = ['load_config', 'save_config', 'CONFIG_DIR', 'CONFIG_FILE']