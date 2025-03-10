# app/api/v1/endpoints/notifications.py
import logging
from typing import Optional
from uuid import UUID

from core.database import get_mongo_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.notification import (
    NotificationRequest,
    NotificationStatus,
    UserNotificationResponse,
)
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import Counter, Histogram
from services.notification_service import NotificationService

router = APIRouter()
logger = logging.getLogger(__name__)

# Счетчик количества созданных уведомлений
NOTIFICATIONS_CREATED = Counter(
    "notifications_created_total", "Total number of notifications created"
)

# Счетчик запросов на получение уведомлений
USER_NOTIFICATIONS_REQUESTS = Counter(
    "user_notifications_requests_total", "Total number of user notification requests"
)

# Гистограмма времени обработки запроса
REQUEST_LATENCY = Histogram(
    "notification_request_latency_seconds",
    "Latency of notification requests",
)


async def get_notification_service(
    db: AsyncIOMotorClient = Depends(get_mongo_db),
) -> NotificationService:
    """Dependency для получения сервиса уведомлений."""
    return NotificationService(db)


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Создание уведомления",
    description="Создание уведомления через админку или другие сервисы. "
    "Поддерживает отложенную отправку и повторяющиеся уведомления.",
)
@REQUEST_LATENCY.time()
async def create_notification(
    notification: NotificationRequest,
    service: NotificationService = Depends(get_notification_service),
):
    """
    Создание нового уведомления.

    - Можно указать шаблон или передать текст напрямую
    - Поддерживает отложенную отправку
    - Поддерживает повторяющиеся уведомления
    """
    try:
        # Создаем уведомление через сервис
        notification_obj = await service.create_notification(notification)

        return {"status": "success", "notification": str(notification_obj)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification",
        )


@router.get(
    "/user/{user_id}",
    response_model=list[UserNotificationResponse],
    summary="Получение уведомлений пользователя",
    description="Получение списка уведомлений пользователя с возможностью фильтрации",
)
@REQUEST_LATENCY.time()
async def get_user_notifications(
    user_id: UUID,
    limit: int = Query(50, gt=0, le=100),
    skip: int = Query(0, ge=0),
    status: Optional[NotificationStatus] = None,
    service: NotificationService = Depends(get_notification_service),
):
    """
    Получение уведомлений пользователя.

    - Поддерживает пагинацию
    - Фильтрация по статусу
    - Сортировка по времени создания (новые первыми)
    """
    try:
        return await service.get_user_notifications(
            user_id=user_id, limit=limit, skip=skip
        )

    except Exception as e:
        logger.error(
            "Error fetching notifications for user user_id = %(user_id)s: e = %(e)s",
            {"user_id": user_id, "e": e},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications",
        )


@router.get("/health", tags=["health"])
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok"}


@router.get("/ready", tags=["health"])
async def readiness_check(service: NotificationService = Depends(get_notification_service)):
    """Проверяет доступность зависимостей (например, RabbitMQ и MongoDB)"""
    if await service.check_dependencies():
        return {"status": "ready"}
    return {"status": "not ready"}, 503
