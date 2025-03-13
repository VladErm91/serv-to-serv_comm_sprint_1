# app/main.py
import logging
from contextlib import asynccontextmanager

from api.middleware import setup_middleware
from api.v1.api import api_router
from core.config import settings
from core.database import mongodb_manager
from core.logger import setup_logging
from core.rabbitmq import rabbitmq_manager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    logger.info("Starting up notification service...")

    try:
        await mongodb_manager.connect()  # Подключение к MongoDB
        await rabbitmq_manager.connect()  # Подключение к RabbitMQ
    except Exception as e:
        logger.error(f"Failed to connect to services: {e}")
        raise

    try:
        yield
    finally:
        # Закрытие ресурсов
        await rabbitmq_manager.close()  # Закрытие соединения с RabbitMQ
        await mongodb_manager.close()  # Закрытие соединения с MongoDB
        logger.info("Shutting down notification service...")


app = FastAPI(
    title="Notification Service API",
    description="API для отправки и управления уведомлениями",
    version="1.0.0",
    docs_url="/api/notifications_api/oopenapi",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Настройка CORS
allow_origins = settings.cors_origins or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка middleware
setup_middleware(app)

# Подключение роутеров
app.include_router(api_router, prefix="/api/notifications_api/v1")
