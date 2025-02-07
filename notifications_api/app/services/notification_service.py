import base64
from datetime import datetime
from logging import getLogger
from typing import Optional
from uuid import UUID, uuid4

from core.config import settings
from core.database import (
    convert_binary_to_uuid,
    convert_uuid_to_binary,
    mongodb_manager,
)
from core.rabbitmq import rabbitmq_manager
from models.notification import Notification, NotificationRequest

logger = getLogger(__name__)


def process_notification(notification: Notification):
    logger.debug("Обработка уведомления")
    logger.info(f"Отправка уведомления: {notification}")
    logger.debug("Уведомление обработано")


class NotificationService:
    def __init__(self, db):
        self.db = db

    async def create_notification(
        self, notification: NotificationRequest
    ) -> Notification:
        try:
            logger.info("Начало создания уведомления")

            # Ensure the notification has an ID
            if not notification.id:
                notification.id = uuid4()

            # Преобразуем UUID в бинарный формат
            notification_dict = notification.model_dump()
            notification_dict["id"] = convert_uuid_to_binary(notification.id)
            notification_dict["recipients"] = [
                convert_uuid_to_binary(recipient)
                for recipient in notification_dict["recipients"]
            ]

            logger.info(f"Данные уведомления для mongo: {notification_dict}")

            # Сохраняем уведомление в базу данных
            db = mongodb_manager.get_db()  # Получаем базу данных через менеджер
            await db[settings.notifications_collection].insert_one(notification_dict)
            logger.info("Уведомление успешно сохранено в базу данных")

            # Преобразуем бинарные данные в base64 для отправки в RabbitMQ
            notification_dict["id"] = base64.b64encode(notification_dict["id"]).decode(
                "utf-8"
            )

            notification_dict["recipients"] = [
                base64.b64encode(recipient).decode("utf-8")
                for recipient in notification_dict["recipients"]
            ]

            # Преобразуем ObjectId в строку для отправки в RabbitMQ
            if "_id" in notification_dict:
                notification_dict["_id"] = str(notification_dict["_id"])

            # Преобразуем datetime в строку ISO 8601
            if "scheduled_time" in notification_dict and isinstance(
                notification_dict["scheduled_time"], datetime
            ):
                notification_dict["scheduled_time"] = notification_dict[
                    "scheduled_time"
                ].isoformat()
            logger.info(f"Данные уведомления для rabbit: {notification_dict}")

            # Отправляем уведомление в очередь RabbitMQ
            await rabbitmq_manager.send_to_queue(
                settings.rabbitmq_queue, notification_dict
            )
            logger.info("Уведомление успешно отправлено в очередь RabbitMQ")

            return notification_dict

        except Exception as e:
            logger.error(f"Ошибка при создании уведомления: {e}", exc_info=True)
            raise

    async def schedule_notification(self, notification: NotificationRequest) -> None:
        """
        Обрабатывает отложенные и повторяющиеся уведомления.
        Пока что просто отправляет уведомление в очередь.
        """
        try:
            # Ensure the notification has an ID
            if not notification.id:
                notification.id = uuid4()

            # Преобразуем UUID в бинарный формат
            notification_dict = notification.model_dump()
            notification_dict["id"] = convert_uuid_to_binary(notification.id)
            notification_dict["recipients"] = [
                convert_uuid_to_binary(recipient)
                for recipient in notification_dict["recipients"]
            ]

            logger.info(f"Данные уведомления для mongo: {notification_dict}")

            # Сохраняем уведомление в базу данных
            db = mongodb_manager.get_db()  # Получаем базу данных через менеджер
            await db[settings.notifications_collection].insert_one(notification_dict)
            logger.info("Уведомление успешно сохранено в базу данных")

            # Преобразуем бинарные данные в base64 для отправки в RabbitMQ
            notification_dict["id"] = base64.b64encode(notification_dict["id"]).decode(
                "utf-8"
            )
            notification_dict["recipients"] = [
                base64.b64encode(recipient).decode("utf-8")
                for recipient in notification_dict["recipients"]
            ]

            # Преобразуем ObjectId в строку для отправки в RabbitMQ
            if "_id" in notification_dict:
                notification_dict["_id"] = str(notification_dict["_id"])
            logger.info("")
            # Преобразуем datetime в строку ISO 8601
            if "scheduled_time" in notification_dict and isinstance(
                notification_dict["scheduled_time"], datetime
            ):
                notification_dict["scheduled_time"] = notification_dict[
                    "scheduled_time"
                ].isoformat()
            logger.debug(f"Данные уведомления для rabbit {notification_dict}")
            
            # Отправляем уведомление в очередь
            await rabbitmq_manager.send_to_queue(
                settings.rabbitmq_queue, notification_dict
            )
            logger.info("Уведомление успешно отправлено в очередь RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при планировании уведомления: {e}", exc_info=True)
            raise

    async def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        try:
            # Преобразуем UUID в бинарный формат для поиска
            binary_id = convert_uuid_to_binary(notification_id)
            db = mongodb_manager.get_db()  # Получаем базу данных через менеджер
            notification = await db[settings.notifications_collection].find_one(
                {"id": binary_id}
            )
            if notification:
                # Преобразуем бинарный формат обратно в UUID
                notification["id"] = convert_binary_to_uuid(notification["id"])
                notification["recipients"] = [
                    convert_binary_to_uuid(recipient)
                    for recipient in notification["recipients"]
                ]
                logger.info(f"Данные уведомления для mongo: {notification}")
                return Notification(**notification)
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении уведомления: {e}", exc_info=True)
            raise
