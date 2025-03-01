import asyncio
import json
import logging
import os
import smtplib
import time
from email.message import EmailMessage

from aio_pika import Channel
from core.rabbitmq import rabbitmq_manager
from core.settings import settings
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

load_dotenv(dotenv_path=parent_dir)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def send_email(
    login: str,
    domain: str,
    password: str,
    smtp_port: int,
    smtp_host: str,
    msg: dict,
    max_retries=3,
) -> bool:
    EMAIL = f"{login}@{domain}"
    server = smtplib.SMTP_SSL(smtp_host, smtp_port)
    for attempt in range(max_retries):
        try:
            server.login(login, password)
            message = EmailMessage()
            message["From"] = EMAIL
            recipient = msg["email"]
            message["To"] = recipient
            message["Subject"] = msg["subject"]
            context = msg["text"]
            message.add_alternative(context, subtype="html")
            server.sendmail(EMAIL, recipient, message.as_string())
            logger.info(f"Письмо успешно отправлено с {attempt + 1} попытки")
            return True
        except smtplib.SMTPException as exc:
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.warning(
                    f"Не удалось отправить письмо. Попытка №{attempt + 1}. Причина: {exc}. "
                    f"Повторная попытка через {wait_time} сек."
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"Не удалось отправить письмо после {max_retries} попыток. Причина: {exc}"
                )
                raise
        finally:
            server.close()


def handler(
    ch: Channel,
    method,
    properties,
    body: bytes,
) -> None:
    logger.info("Получено сообщение")
    try:
        message = json.loads(body)
        logger.info(f"Тело сообщения: {message}")
        send_email(
            login=settings.email.login,
            domain=settings.email.domain,
            password=settings.email.password,
            smtp_host=settings.email.smtp_host,
            smtp_port=465,
            msg=message,
        )
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON")
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    try:
        logger.info("Starting sender...")
        asyncio.run(rabbitmq_manager.start_consuming(settings.mq.queue, handler))

    except KeyboardInterrupt:
        rabbitmq_manager.close()
    finally:
        rabbitmq_manager.close()
        logger.info("Соединение с RabbitMQ закрыто")
