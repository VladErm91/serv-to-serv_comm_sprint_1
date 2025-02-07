from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Template(BaseModel):
    slug: Optional[str]
    title: Optional[str]
    description: Optional[str] = None
    context: Optional[str] = None


class Notification(BaseModel):
    id: UUID
    delivery_type: str
    status: str
    subject: Optional[str]
    template_id: Optional[str]
    recipients: list[UUID]
    subject: Optional[str]
    scheduled_time: Optional[datetime] = None
    repeat_interval: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]


class NotificationMessage(BaseModel):
    id: UUID
    delivery_type: str
    emails: list[str]
    subject: Optional[str]
    context: Optional[str]
    scheduled_time: Optional[datetime] = None
    repeat_interval: Optional[str] = None
