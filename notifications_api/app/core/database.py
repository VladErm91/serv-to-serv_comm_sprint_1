# app/core/database.py
import logging
from uuid import UUID

from bson import Binary
from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class MongoDBConnectionManager:
    """
    Класс для управления подключением к MongoDB.
    """

    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self) -> None:
        """
        Асинхронно подключается к MongoDB.
        """
        try:
            # Формируем URL для подключения
            mongo_url = settings.mongodb_url

            # Устанавливаем соединение с MongoDB
            self.client = AsyncIOMotorClient(mongo_url, uuidRepresentation="standard")
            self.db = self.client[settings.mongodb_database]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self) -> None:
        """
        Асинхронно закрывает соединение с MongoDB.
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed successfully")

    def get_db(self):
        """
        Возвращает текущую базу данных MongoDB.
        """
        if self.db is None:  # Используем явное сравнение с None
            raise RuntimeError("MongoDB connection is not established.")
        return self.db


# Создание менеджера подключения
mongodb_manager = MongoDBConnectionManager()


async def get_mongo_db() -> AsyncIOMotorClient:
    uri = settings.mongodb_url
    client = AsyncIOMotorClient(uri)
    return client


def convert_uuid_to_binary(uuid_obj: UUID) -> Binary:
    """
    Преобразует UUID в бинарный формат для MongoDB.

    :param uuid_obj: UUID-объект.
    :return: Binary-объект.
    """
    try:
        return Binary.from_uuid(uuid_obj)
    except Exception as e:
        logger.error(f"Failed to convert UUID to binary: {e}")
        raise


def convert_binary_to_uuid(binary_obj: Binary | UUID) -> UUID:
    """
    Преобразует бинарный формат MongoDB обратно в UUID.

    :param binary_obj: Binary или UUID-объект.
    :return: UUID-объект.
    """
    try:
        if isinstance(binary_obj, Binary):
            return binary_obj.as_uuid()
        elif isinstance(binary_obj, UUID):
            return binary_obj
        else:
            raise TypeError(
                f"Invalid type for binary_obj: {type(binary_obj)}. Expected Binary or UUID."
            )
    except Exception as e:
        logger.error(f"Failed to convert binary to UUID: {e}")
        raise
