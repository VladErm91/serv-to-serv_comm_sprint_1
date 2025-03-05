import asyncio
import json
import logging

from aio_pika import Channel, Message, RobustConnection, connect_robust
from aio_pika.exceptions import AMQPConnectionError
from core.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQConnectionManager:
    """
    Класс для управления подключением к RabbitMQ.
    """

    def __init__(self):
        self.connection: RobustConnection | None = None
        self.channel: Channel | None = None

    async def start_consuming(self, queue_name: str, callback) -> None:
        """
        Устанавливает соединение с RabbitMQ.
        """
        try:
            self.connection = await connect_robust(settings.mq.rabbitmq_url, loop=None)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            logger.info("RabbitMQ connection established successfully")

            queue = await self.channel.declare_queue(name=queue_name, durable=True)

            logger.info("Очередь объявлена, начинаем прослушивание сообщений...")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            payload = json.loads(message.body.decode())
                            logger.info("Получено сообщение:", payload, flush=True)
                            await callback(payload)
                        except Exception as e:
                            logger.info(
                                f"Ошибка при обработке сообщения RabbitMQ: {e}",
                                flush=True,
                            )
                logger.info(f"Waiting for messages in queue '{queue_name}'...")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def close(self) -> None:
        """
        Закрывает соединение с RabbitMQ.
        """
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed successfully")

    async def establish_connection_with_retry(
        self, url: str, retries: int = 30, delay: int = 5
    ):
        logger.info("Начинаем попытки подключения к RabbitMQ...", flush=True)
        url = settings.rabbitmq_url
        for attempt in range(1, retries + 1):
            try:
                connection = await connect_robust(url, loop=None)
                logger.info(
                    f"Подключение к RabbitMQ успешно установлено на попытке {attempt}.",
                    flush=True,
                )
                return connection
            except AMQPConnectionError as e:
                logger.error(
                    f"Попытка {attempt}: не удалось подключиться ({e}). Повтор через {delay} секунд...",
                    flush=True,
                )
                await asyncio.sleep(delay)
                raise RuntimeError(
                    "Не удалось установить соединение с RabbitMQ после нескольких попыток."
                )

    async def send_to_queue(self, queue_name: str, message: dict) -> None:
        """
        Отправляет сообщение в указанную очередь RabbitMQ.

        :param queue_name: Имя очереди.
        :param message: Сериализуемый словарь для отправки.
        """
        if not self.channel:
            raise RuntimeError(
                "RabbitMQ channel is not initialized. Call 'connect' first."
            )
        try:
            await self.channel.declare_queue(queue_name, durable=True)
            await self.channel.default_exchange.publish(
                Message(
                    json.dumps(message).encode(),
                    delivery_mode=2,  # Установить сообщение как persistent
                ),
                routing_key=queue_name,
            )
        except Exception as e:
            logger.error(f"Failed to send message to RabbitMQ: {e}")
            raise


# Инициализация менеджера подключения
rabbitmq_manager = RabbitMQConnectionManager()
