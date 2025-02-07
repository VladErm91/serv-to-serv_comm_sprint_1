# django_admin/app/notifications/services.py
import logging

import requests
from django.conf import settings

from .notification import Notification

logger = logging.getLogger(__name__)


def send_notification_to_api(notification_id):
    """
    Отправляет уведомление в сервис API.
    """
    try:
        # Получаем уведомление из базы данных
        notification = Notification.objects.get(id=notification_id)

        # Формируем payload для отправки в сервис API
        payload = {
            "recipients": notification.recipients_ids,  # Список ID пользователей
            "template_id": str(notification.template.slug),  # ID шаблона
            "delivery_type": notification.delivery_type,  # Способ доставки (email, sms, push)
            "scheduled_time": (
                notification.scheduled_time.isoformat()
                if notification.scheduled_time
                else None
            ),  # Время отправки
            "repeat_interval": (
                notification.repeat_type
                if notification.repeat_type != "* * * * *"
                else None
            ),  # Интервал повторения
        }
        logger.info(f"Sending notification {notification_id} to API: {payload}")
        # Отправляем запрос в сервис API
        response = requests.post(
            f"{settings.API_URL}/notifications/",  # URL сервиса API
            json=payload,
        )

        # Проверяем статус ответа
        if response.status_code == 200:
            logger.info(f"Notification {notification_id} sent to API successfully")
        else:
            logger.error(
                f"Failed to send notification {notification_id} to API. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} does not exist")
    except Exception as e:
        logger.error(f"Error sending notification {notification_id} to API: {e}")
