import logging
from uuid import UUID

from httpx import AsyncClient, HTTPStatusError

from utils.schemas import Notification, NotificationMessage, Template
from core.config import settings

logger = logging.getLogger(__name__)


async def get_user_data(user_id: UUID):
    # Здесь должна быть логика получения данных пользователя из базы данных
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{settings.auth_service_url}{user_id}")
            response.raise_for_status()
            user_data = response.json()
            return user_data
    except HTTPStatusError as exc:
        logger.error(f"Ошибка запроса: {exc.response.status_code} {exc.response.text}")
        raise
    except Exception as error:
        logger.error(f"Данные пользователя не удалось извлечь: {error}")
        raise


async def get_template_data(template_id: str):
    # Логика получения данных пользователя из эндпоинта
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{settings.template_service_url}{template_id}")
            response.raise_for_status()
            template_data = response.json()
            return template_data
    except HTTPStatusError as exc:
        logger.error(f"Ошибка запроса: {exc.response.status_code} {exc.response.text}")
        raise
    except Exception as error:
        logger.error(f"Данные шаблона не удалось извлечь: {error}")
        raise


def render_template(template_data: Template, username: str):
    text = template_data.get("context", {})
    # Простая реализация подстановки данных в шаблон
    return text.format(**username)


def can_receive_notification(userdata: dict, delivery_type: str):
    settings = userdata["notification_settings"]
    if delivery_type == "email":
        return settings.get("email_enabled", False)
    elif delivery_type == "push":
        return settings.get("push_enabled", False)
    return False


def select_notification_queue(notification_data: Notification):
    if (
        notification_data["scheduled_time"]
        is None & notification_data["repeat_interval"]
        is None
    ):
        if notification_data["delivery_type"] == "email":
            queue_name = settings.sender_queue
        elif notification_data["delivery_type"] == "push":
            queue_name = settings.websocket_queue
    else:
        queue_name = settings.scheduled_queue
    return queue_name


def process_notification(notification_data: Notification):
    recipients = notification_data["recipients"]
    logger.info("Processing notification for n = %(n)d recipients", {"n": len(recipients)})
    try:
        emails = []
        if len(recipients) > 1:
            for user_id in recipients:
                userdata = get_user_data(user_id)
                emails.append(userdata["email"])
                if not can_receive_notification(
                    userdata, notification_data["delivery_type"]
                ):
                    logger.info(
                        "User username = %(username)s has disabled delivery_type =%(delivery_type)s notifications",  
                        {"username": userdata["username"], "delivery_type": notification_data["delivery_type"]}
                    )
            text = get_template_data(notification_data["template_id"])
        else:
            userdata = get_user_data(recipients[0])
            if not can_receive_notification(
                userdata, notification_data["delivery_type"]
            ):
                logger.info(
                    "User username = %(username)s has disabled delivery_type =%(delivery_type)s notifications",  
                    {"username": userdata["username"], "delivery_type": notification_data["delivery_type"]}
                )
            username = userdata["username"]
            emails.append(userdata["email"])
            template_data = get_template_data(notification_data["template_id"])
            text = render_template(template_data, username)

        message: NotificationMessage = {
            notification_data["id"],
            notification_data["delivery_type"],
            emails,
            notification_data["subject"],
            text,
            notification_data["scheduled_time"],
            notification_data["repeat_interval"],
        }
        return message
    except Exception as error:
        logger.error(f"Failed to send notification to queue: {error}")
