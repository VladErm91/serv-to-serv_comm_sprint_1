# app/core/celery.py
import logging

from celery import Celery
from core.config import settings
from services.notification_service import process_notification

logger = logging.getLogger(__name__)

app = Celery(
    "notification_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Конфигурация Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
)


@app.task(bind=True, max_retries=3)
def schedule_notification(self, notification_data):
    recipients = notification_data["recipients"]
    logger.info(f"Processing notification for {len(recipients)} recipients")
    for user_id in recipients:
        try:
            process_notification(user_id, notification_data)
            logger.info(f"Notification processed for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to process notification for user {user_id}: {e}")
            self.retry(exc=e, countdown=60)  # Повторная попытка через 60 секунд


@app.task(bind=True, max_retries=3)
def repeat_notification(self, notification_data, interval):
    try:
        logger.info(f"Repeating notification with interval {interval}")
        schedule_notification.delay(notification_data)
        self.apply_async(args=[notification_data, interval], countdown=interval)
    except Exception as e:
        logger.error(f"Failed to repeat notification: {e}")
        self.retry(exc=e, countdown=60)  # Повторная попытка через 60 секунд
