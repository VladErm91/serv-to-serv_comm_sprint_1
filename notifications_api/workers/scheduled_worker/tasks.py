import json
import logging
from datetime import datetime

from celery import shared_task
from celery.exceptions import Ignore

from core.config import settings
from core.rabbitmq import rabbitmq_manager

logger = logging.getLogger(__name__)


def get_final_delivery_queue(notification_data):
    """Определяем финальную очередь (email или push), когда пришло время отправки."""
    delivery_type = notification_data.get("delivery_type", "email")
    if delivery_type == "push":
        return settings.websocket_queue
    # По умолчанию, считаем, что email
    return settings.sender_queue


@shared_task(bind=True)
def schedule_notification(self, notification_data: dict):
    """
    Таска, которая вызывается Celery-воркером.
    Проверяет, пришло ли время отправлять (scheduled_time).
    Если нет — делает retry.
    Если да — отправляет в нужную очередь (email/push).
    Если есть repeat_interval — планирует следующую задачу.
    """
    try:
        scheduled_time = notification_data.get("scheduled_time")
        repeat_interval = notification_data.get("repeat_interval")

        if scheduled_time:
            # Логика проверки времени
            dt_scheduled_time = datetime.fromisoformat(scheduled_time)
            now = datetime.utcnow()
            if dt_scheduled_time > now:
                eta_seconds = (dt_scheduled_time - now).total_seconds()
                self.retry(countdown=eta_seconds, max_retries=0)
                return

        # Если мы здесь, значит либо scheduled_time нет, либо оно наступило
        # => отправляем в финальную очередь
        final_queue = get_final_delivery_queue(notification_data)

        # Важно: не забываем сериализовать данные
        rabbitmq_manager.send_to_queue(json.dumps(notification_data), final_queue)

        # Если есть repeat_interval, запланируем следующий запуск
        if repeat_interval:
            self.apply_async(args=[notification_data], countdown=repeat_interval)

    except Exception as e:
        logger.error(f"Ошибка schedule_notification: {e}")
        raise Ignore()
