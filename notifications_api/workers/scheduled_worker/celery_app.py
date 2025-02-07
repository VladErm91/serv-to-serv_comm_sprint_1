from celery import Celery

from core.config import settings

# Создаём экземпляр Celery-приложения
app = Celery(
    "scheduled_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
