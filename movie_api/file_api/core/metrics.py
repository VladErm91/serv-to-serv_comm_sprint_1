from typing import Callable

from prometheus_client import Counter
from prometheus_fastapi_instrumentator.metrics import Info

# Метрика для подсчёта количества загрузок файлов по типам
file_upload_requests_total = Counter(
    "file_upload_requests_total", "Total number of file upload requests", ["file_type"]
)


def instrument_file_uploads() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        # Фильтруем только POST-запросы к /upload/
        if info.request.method == "POST" and info.request.url.path == "/upload/":
            file_type = "unknown"

            # Получаем content-type из заголовков запроса
            content_type = info.request.headers.get("content-type", "")
            if ";" in content_type:
                file_type = content_type.split(";")[0]
            else:
                file_type = content_type

            # Увеличиваем счётчик для конкретного типа файла
            file_upload_requests_total.labels(file_type=file_type).inc()

    return instrumentation
