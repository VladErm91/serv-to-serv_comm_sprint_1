import asyncio
import json
import logging

from core.config import settings
from core.rabbitmq import rabbitmq_manager
from services.worker_service import process_notification, select_notification_queue

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_queue_message(method, properties, body: bytes):
    """
    Обработка сообщения из очереди первичной очереди и отправка его в очередь для сендеров или шедулера.
    """
    try:
        notification_data = json.loads(body)
        user_message = process_notification(notification_data)
        queue_name = select_notification_queue(notification_data)
        
        await rabbitmq_manager.send_to_queue(user_message, queue_name)

        logger.info("Notification processed id = %(id)s", {"id": notification_data['id']})
    except Exception as e:
        logger.error("Failed to process notification id = %(id)s: e =%(e)s", {"id": notification_data['id'], "e": e})
        # Можно добавить повторную попытку или отправку в очередь ошибок

    except json.JSONDecodeError:
        logger.error("Failed to decode message from queue")
    except KeyError:
        logger.error("Invalid message format: missing 'recipients' field")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    try:
        logger.info("Starting worker...")
        asyncio.run(
            rabbitmq_manager.start_consuming(settings.queue_name, process_queue_message)
        )
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
