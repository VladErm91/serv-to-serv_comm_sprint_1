from pydantic import Field
from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):

    rabbitmq_url: str = Field(
        default="amqp://rmuser:rmpassword@rabbitmq:5672//", env="RABBITMQ_URL"
    )
    sender_queue: str = Field(default="sender", env="RABBITMQ_QUEUE_SEND")
    websocket_queue: str = Field(default="websockets", env="RABBITMQ_QUEUE_WS")
    scheduled_queue: str = Field(
        default="scheduled",
        env="RABBITMQ_QUEUE_SCHEDULED",
    )

    celery_broker_url: str = Field(
        default="amqp://rmuser:rmpassword@rabbitmq:5672//",
        env="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://redis:6379/0",
        env="CELERY_RESULT_BACKEND",
    )


settings = WorkerSettings()
