import os
from dotenv import load_dotenv
import sys

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена вашего бота в Telegram
TELEGRAMM_TOKEN = os.getenv('TELEGRAMM_TOKEN')
if TELEGRAMM_TOKEN is None:
    print("Ошибка: Токен Telegram бота не найден в переменных окружения.")
    sys.exit(1)

# Получение токена вашей страницы в VK
VK_TOKEN = os.getenv('VK_TOKEN')
if VK_TOKEN is None:
    print("Ошибка: Токен вашей страницы в VK не найден в переменных окружения.")
    sys.exit(1)