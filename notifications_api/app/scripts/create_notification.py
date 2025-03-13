import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import requests

logger = logging.getLogger(__name__)
# URL API
API_URL = "http://127.0.0.1:8000/api/v1/notifications/"

# Данные для уведомления
notification_data = {
    "user_id": str(uuid4()),  # Генерируем случайный UUID для пользователя
    "template_id": str(uuid4()),  # Генерируем случайный UUID для шаблона
    "subject": "Test Notification",
    "text": "This is a test notification.",
    "delivery_type": "email",
    "context": {"user_name": "John"},
    "scheduled_at": (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat(),  # Отложенное уведомление
}

# Отправляем запрос на создание уведомления
response = requests.post(API_URL, json=notification_data)

# Выводим результат
if response.status_code == 200:
    logger.info("Notification created successfully!")
    logger.info(response.json())
else:
    logger.info("Failed to create notification.")
    logger.info(response.status_code, response.text)
