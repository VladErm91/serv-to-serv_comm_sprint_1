import asyncio
import json
import logging

from core.config import settings
from core.rabbitmq import rabbitmq_manager
from tasks import schedule_notification

logger = logging.getLogger(__name__)


async def process_scheduled_message(method, properties, body):
    """
    Обработчик сообщений из очереди scheduled_queue.
    Здесь мы просто передаём полученные данные в Celery-таску schedule_notification,
    которая уже сама разберётся, когда именно отправлять конечное уведомление.
    """
    try:
        notification_data = json.loads(body)

        schedule_notification.delay(notification_data)

        logger.info(
            f"Получено отложенное сообщение (id={notification_data.get('id')}). "
            f"Поручено Celery-таске schedule_notification."
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения из scheduled_queue: {e}")


if __name__ == "__main__":
    try:
        logger.info("Запуск сервиса отложенной отправки (scheduled_service)...")
        asyncio.run(
            rabbitmq_manager.start_consuming(
                settings.scheduled_queue, process_scheduled_message
            )
        )
    except KeyboardInterrupt:
        logger.info("Сервис отложенной отправки остановлен пользователем")
    except Exception as e:
        logger.error(f"Сервис отложенной отправки аварийно завершился: {e}")
