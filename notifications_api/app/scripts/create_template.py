import logging

import requests

logger = logging.getLogger(__name__)

# URL API
API_URL = "http://127.0.0.1:8000/api/v1/templates/"

# Данные для шаблона
template_data = {
    "name": "Welcome Email",
    "content": "Привет, {{user_name}}! Добро пожаловать в наш сервис.",
}

# Отправляем запрос на создание шаблона
response = requests.post(API_URL, json=template_data)

# Выводим результат
if response.status_code == 200:
    logger.info("Template created successfully!")
    logger.info(response.json())
else:
    logger.info("Failed to create template.")
    logger.info(response.status_code, response.text)
