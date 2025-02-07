# app/core/config.py
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project settings
    project_name: str = "Notification Service"
    debug: bool = Field(default=False, env="DEBUG")

    # MongoDB settings
    mongodb_url: str = "mongodb://mongodb:27017/notifications"
    mongodb_database: str = Field(default="notifications", env="MONGO_DB")
    mongodb_user: str = Field(default="admin", env="MONGO_USER")
    mongodb_password: str = Field(default="password123", env="MONGO_PASSWORD")

    # Collections
    notifications_collection: str = "notifications"
    events_collection: str = "events"

    # RabbitMQ settings
    rabbitmq_host: str = Field(default="rabbitmq", env="RABBITMQ_HOSTNAME")
    rabbitmq_port: int = Field(default=int("5672"), env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(
        default="rmuser",
        env="RABBITMQ_DEFAULT_USER",
    )
    rabbitmq_pass: str = Field(
        default="rmpassword",
        env="RABBITMQ_DEFAULT_PASS",
    )
    rabbitmq_queue: str = Field(default="notification_queue", env="RABBITMQ_QUEUE")
    rabbitmq_exchange: str = "notification_exchange"
    rabbitmq_routing_key: str = "notification.#"

    # Celery settings
    celery_broker_url: str = Field(
        default="amqp://rmuser:rmpassword@rabbitmq:5672//",
        env="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="rpc://rmuser:rmpassword@rabbitmq:5672//",
        env="CELERY_RESULT_BACKEND",
    )
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_timezone: str = Field(default="UTC", env="TIME_ZONE")
    celery_task_routes: dict[str, Any] = {
        "app.tasks.*": {"queue": "notification_queue"}
    }

    # API settings
    api_v1_prefix: str = "/api/v1"

    # Admin service settings
    admin_service_url: str = Field(
        default="http://django_admin:8081",
        env="AUTH_API_LOGIN_URL",
    )
    admin_service_timeout: int = 5  # seconds

    # Template settings
    template_cache_ttl: int = 300  # 5 minutes
    template_cache_size: int = 100  # Maximum number of templates to cache

    # Notification settings
    max_retries: int = 3  # Maximum number of retries for failed notifications
    retry_delay: int = 300  # 5 minutes between retries
    batch_size: int = 100  # Number of notifications to process in one batch

    # CORS settings
    # CORS settings
    cors_origins: list[str] = Field(
        default="localhost,127.0.0.1".split(","),
        env="ALLOWED_HOSTS",
    )

    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@{self.rabbitmq_host}:{self.rabbitmq_port}//"

    @property
    def mongodb_notifications_collection(self) -> str:
        return f"{self.mongodb_database}.{self.notifications_collection}"

    @property
    def mongodb_events_collection(self) -> str:

        return f"{self.mongodb_database}.{self.events_collection}"


settings = Settings()
