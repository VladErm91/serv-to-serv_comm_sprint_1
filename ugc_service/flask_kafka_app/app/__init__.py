# flask_kafka_app/app/__init__.py
import logging

from flasgger import Swagger
from flask import Flask

from .config import settings
from .create_topics import create_topics_if_not_exists
from .routes import init_routes
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)
    # Настройка приложения
    app.config.from_object(settings)

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    metrics = PrometheusMetrics(app)
    # Создание топиков Kafka при старте
    create_topics_if_not_exists()

    # Инициализация Swagger
    Swagger(app)

    # Инициализация маршрутов
    init_routes(app)

    return app
