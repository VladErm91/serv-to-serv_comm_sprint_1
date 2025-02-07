from pydantic import Field
from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):

    rabbitmq_url: str = Field(
        default="amqp://rmuser:rmpassword@rabbitmq:5672//",
        env="RABBITMQ_URL",
    )
    queue_name: str = Field(default="notifications", env="RABBITMQ_QUEUE")
    sender_queue: str = Field(default="sender", env="RABBITMQ_QUEUE_SEND")
    websocket_queue: str = Field(default="websockets", env="RABBITMQ_QUEUE_WS")
    scheduled_queue: str = Field(
        default="scheduled",
        env="RABBITMQ_QUEUE_SCHEDULED",
    )
    auth_service_url: str = Field(
        default="http://api/auth/v1/user:8080/users/{user_id}",
        # TODO добавить ендпоинт в сервис авторизации
        env="AUTH_SERVICE_URL",
    )
    template_service_url: str = Field(
        default="http://api/notifications_api/v1/templates/{template_id}",
        env="TEMPLATE_URL",
    )


settings = WorkerSettings()
