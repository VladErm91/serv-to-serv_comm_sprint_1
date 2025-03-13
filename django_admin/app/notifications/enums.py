# django_admin/app/notifications/enums.py

from enum import Enum


class BaseEnum(str, Enum):
    @classmethod
    def choice(cls) -> list:
        return [(item.value, item.name) for item in cls]


class DeliveryType(BaseEnum):
    """
    Виды отправки
    """

    EMAIL: str = "email"
    PUSH: str = "push"


class Status(BaseEnum):
    """
    Статусы обработки уведомления
    """

    SENT: str = "sent"
    PENDING: str = "attempting"
    DELIVERED: str = "delivered"
    FAILED: str = "failed"
