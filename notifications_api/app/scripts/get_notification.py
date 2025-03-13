import logging
from uuid import UUID

import requests

logger = logging.getLogger(__name__)

# URL API
API_URL = "http://127.0.0.1:8000/api/v1/notifications/"

# ID уведомления (замени на реальный ID)
notification_id = UUID("ваш-uuid-уведомления")

# Отправляем запрос на получение уведомления
response = requests.get(f"{API_URL}{notification_id}")

# Выводим результат
if response.status_code == 200:
    logger.info("Notification retrieved successfully!")
    logger.info(response.json())
else:
    logger.info("Failed to retrieve notification.")
    logger.info(response.status_code, response.text)
