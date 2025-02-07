# app/models/notification.py

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class DeliveryType(str, Enum):
    """Типы доставки уведомлений."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Статусы уведомлений."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Template(BaseModel):  # модель шаблона
    slug: Optional[str]
    title: Optional[str]
    description: Optional[str] = None
    context: Optional[str] = None


class NotificationRequest(BaseModel):
    """Модель для создания уведомления."""

    id: Optional[UUID] = Field(default_factory=uuid4)
    recipients: list[UUID]
    template_id: Optional[str] = None  # slug шаблона
    subject: Optional[str] = None
    delivery_type: DeliveryType
    scheduled_time: Optional[datetime] = None
    repeat_interval: Optional[str] = None

    @classmethod  # присвоение идентификатора в виде слага шаблона
    def from_template(cls, template: Template):
        return cls(template_id=template.slug)

    @field_validator("delivery_type", check_fields=True)
    def validate_delivery_type(cls, v):
        if v not in [item.value for item in DeliveryType]:
            raise ValueError(f"Invalid delivery type: {v}")
        return v


class UserNotificationResponse(BaseModel):
    """Модель для ответа на запрос уведомлений пользователя."""

    id: UUID
    subject: str
    delivery_type: DeliveryType
    status: NotificationStatus
    created_at: datetime
    scheduled_time: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class Notification(BaseModel):
    """Модель уведомления для внутреннего использования."""

    id: UUID
    template_id: Optional[str] = None
    subject: Optional[str] = None
    delivery_type: DeliveryType
    status: NotificationStatus = NotificationStatus.PENDING
    recipients: list[UUID]
    scheduled_time: Optional[datetime] = None
    repeat_interval: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
