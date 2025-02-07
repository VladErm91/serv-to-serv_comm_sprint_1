import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

current_dir = os.path.dirname(__file__)  # Получить текущий рабочий каталог
parent_dir = os.path.dirname(current_dir)  # Подняться на уровень выше
load_dotenv(dotenv_path=parent_dir)


class RABBITMQSettings(BaseSettings):
    rabbitmq_url: str = Field(
        default="amqp://rmuser:rmpassword@rabbitmq:5672//", env="RABBITMQ_URL"
    )
    queue: str = Field(default="sender", env="RABBITMQ_QUEUE_SEND")


class EMAILSettings(BaseSettings):
    login: str = Field(default="user", env="EMAIL_LOGIN")
    password: str = Field(default="password", env="EMAIL_PASSWORD")
    domain: str = Field(default="yandex.ru", env="EMAIL_DOMAIN")
    smtp_host: str = Field(default="smtp.yandex.ru", env="EMAIL_SMTP_HOST")
    smpt_port: int = Field(default=465, env="EMAIL_SMTP_PORT")


class Settings(BaseSettings):
    mq: RABBITMQSettings = RABBITMQSettings()
    email: EMAILSettings = EMAILSettings()


settings = Settings(BaseSettings)
