import asyncio
import json
import logging
from uuid import UUID

import aio_pika
from aio_pika.exceptions import AMQPConnectionError
from websockets_manager import manager

logger = logging.getLogger(__name__)


async def establish_connection_with_retry(
    host: str, port: int, login: str, password: str, retries: int = 30, delay: int = 5
):
    logger.info("Начинаем попытки подключения к RabbitMQ...", flush=True)
    for attempt in range(1, retries + 1):
        try:
            connection = await aio_pika.connect_robust(
                host=host, port=port, login=login, password=password
            )
            logger.info(
                f"Подключение к RabbitMQ успешно установлено на попытке {attempt}."
            )
            return connection
        except AMQPConnectionError as e:
            logger.error(
                f"Попытка {attempt}: не удалось подключиться ({e}). Повтор через {delay} секунд..."
            )
            await asyncio.sleep(delay)
    raise RuntimeError(
        "Не удалось установить соединение с RabbitMQ после нескольких попыток."
    )


async def consume_push_notifications(
    host: str = "rabbitmq",
    port: int = 5672,
    login: str = "rmuser",
    password: str = "rmpassword",
    queue_name: str = "websockets",
):
    logger.info("Запуск consume_push_notifications...", flush=True)
    # Устанавливаем соединение с повторными попытками
    connection = await establish_connection_with_retry(
        host=host, port=port, login=login, password=password
    )
    channel = await connection.channel()
    # Объявляем очередь
    queue = await channel.declare_queue(queue_name)
    logger.info("Очередь объявлена, начинаем прослушивание сообщений...", flush=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info("Получено сообщение:", payload, flush=True)
                    user_id_str = payload.get("user_id")
                    text_message = payload.get("text", "Push notification")

                    if not user_id_str:
                        continue

                    user_id = UUID(user_id_str)

                    if manager:
                        await manager.send_personal_message(user_id, text_message)
                    else:
                        logger.info(
                            "WebSocketConnectionManager не инициализирован.", flush=True
                        )

                except Exception as e:
                    logger.error(
                        f"Ошибка при обработке сообщения RabbitMQ: {e}", flush=True
                    )
