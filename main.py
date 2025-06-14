import sys
import os
from pathlib import Path
import argparse
import json

os.environ['PYTHONUTF8'] = '1'

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

with open("src/__init__.py", "w") as f:
    f.write("# Инициализация пакета\n")

from src.database import init_db, DB_PATH

try:
    from src.database import init_db, check_database_health, get_db_stats
    from src.CLI_interface import main as cli_main
    from src.server import start_server
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = [
        'pandas', 'numpy', 'requests', 'cryptography', 
        'matplotlib', 'flask', 'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Отсутствуют пакеты: {', '.join(missing_packages)}")
        return False
    
    logger.info("Все зависимости установлены")
    return True

def check_config():
    """Проверка файла конфигурации"""
    config_paths = ["config.json", "src/config.json"]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                required_keys = [
                    "API_KEY_BYBIT", "API_SECRET_KEY_BYBIT",
                    "API_KEY_OKX", "API_SECRET_KEY_OKX", "API_PASSPHRASE"
                ]
                
                missing_keys = [key for key in required_keys if key not in config]
                
                if missing_keys:
                    logger.error(f"В конфигурации отсутствуют ключи: {', '.join(missing_keys)}")
                    return False
                
                logger.info("Конфигурация корректна")
                return True
                
            except json.JSONDecodeError:
                logger.error(f"Ошибка чтения JSON в файле: {config_path}")
                continue
            except Exception as e:
                logger.error(f"Ошибка при проверке конфигурации: {e}")
                continue
    
    logger.error("Файл конфигурации не найден или некорректен")
    return False

def init_database():
    """Инициализация базы данных"""
    try:
        logger.info("Проверка состояния базы данных...")
        init_db()
        
        health_check = check_database_health()
        if isinstance(health_check, dict) and health_check.get('status') == 'ok':
            logger.info("База данных работает корректно")
            
            stats = get_db_stats()
            if isinstance(stats, dict):
                logs_count = stats.get('logs_count', 0)
                trades_count = stats.get('trades_count', 0)
                logger.info(f"Статистика БД: логи={logs_count}, сделки={trades_count}")
            
            return True
        else:
            logger.error("Проблемы с состоянием базы данных")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при работе с БД: {e}")
        return False

def run_cli():
    """Запуск CLI интерфейса"""
    try:
        logger.info("Запуск CLI интерфейса...")
        start_server()
        cli_main()
    except Exception as e:
        logger.error(f"Ошибка запуска CLI: {e}")
        return False
    return True

def run_web():
    """Запуск только веб-интерфейса"""
    try:
        logger.info("Запуск веб-интерфейса...")
        from src.server import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Ошибка запуска веб-интерфейса: {e}")
        return False
    return True

def run_strategy(strategy_name):
    """Запуск торговой стратегии"""
    try:
        logger.info(f"Запуск стратегии: {strategy_name}")
        if strategy_name == "scalping":
            from src.realtime_engine import run_realtime_trading
            from src.strategies.dynamic_scalping_strategy import generate_signal
            
            params = {
                "sma_window": 20,
                "rsi_window": 14,
                "acceleration_threshold": 0.5,
                "quantity_multiply": 1.5,
                "sma_gap": 0.01,
                "rsi_threshold": 10
            }
            
            run_realtime_trading(generate_signal, params)
        else:
            logger.error(f"Неизвестная стратегия: {strategy_name}")
            return False
    except Exception as e:
        logger.error(f"Ошибка запуска стратегии: {e}")
        return False
    return True

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Торговый бот для криптовалют')
    parser.add_argument('--mode', choices=['init', 'cli', 'web', 'strategy'], 
                       required=True, help='Режим работы')
    parser.add_argument('--strategy', help='Название стратегии (для режима strategy)')
    parser.add_argument('--check-only', action='store_true', 
                       help='Только проверка системы (для режима init)')
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("ЗАПУСК ТОРГОВОГО БОТА")
    logger.info("=" * 50)
    
    logger.info("Проверка системы...")
    
    if not check_dependencies():
        return 1
    
    if not check_config():
        return 1
    
    if not init_database():
        return 1
    
    if args.mode == 'init' and args.check_only:
        logger.info("Проверка системы завершена успешно")
        return 0
    
    if args.mode == 'init':
        logger.info("Инициализация завершена успешно")
        return 0
    elif args.mode == 'cli':
        return 0 if run_cli() else 1
    elif args.mode == 'web':
        return 0 if run_web() else 1
    elif args.mode == 'strategy':
        if not args.strategy:
            logger.error("Для режима strategy необходимо указать --strategy")
            return 1
        return 0 if run_strategy(args.strategy) else 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Работа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)