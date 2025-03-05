# app/core/rabbitmq.py
import json
import logging

from aio_pika import Channel, Message, RobustConnection, connect
from core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQConnectionManager:
    """
    Класс для управления подключением к RabbitMQ.
    """

    def __init__(self):
        self.connection: RobustConnection | None = None
        self.channel: Channel | None = None

    async def connect(self) -> None:
        """
        Устанавливает соединение с RabbitMQ.
        """
        try:
            self.connection = await connect(settings.rabbitmq_url, loop=None)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            logger.info("RabbitMQ connection established successfully")
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
