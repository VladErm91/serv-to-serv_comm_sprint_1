import re
from typing import Callable

from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator.metrics import Info

# Счётчики для запросов к эндпоинтам фильмов
film_requests_total = Counter(
    "film_requests_total",
    "Total number of film-related requests",
    ["endpoint", "method"],
)

film_5xx_errors_total = Counter(
    "film_5xx_errors_total",
    "Total number of 5xx errors for film endpoints",
    ["endpoint", "method", "status_code"],
)

film_request_duration_seconds = Histogram(
    "likes_request_duration_seconds",
    "Duration of like requests",
    ["endpoint", "method"],
)

# Счётчики для запросов к персональным эндпоинтам
person_requests_total = Counter(
    "person_requests_total",
    "Total number of person-related requests",
    ["endpoint", "method"],
)

person_5xx_errors_total = Counter(
    "person_5xx_errors_total",
    "Total number of 5xx errors for person endpoints",
    ["endpoint", "method", "status_code"],
)

person_request_duration_seconds = Histogram(
    "likes_request_duration_seconds",
    "Duration of like requests",
    ["endpoint", "method"],
)


def instrument_person_endpoints() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        person_endpoint_patterns = {
            "/persons/search": r"^/persons/search$",
            "/persons/{person_id}": r"^/persons/[^/]+$",
            "/persons/{person_id}/film": r"^/persons/[^/]+/film/$",
        }

        if info.request.method not in ["GET"]:
            return

        matched_endpoint = None

        for endpoint, pattern in person_endpoint_patterns.items():
            if re.match(pattern, info.request.url.path):
                matched_endpoint = endpoint
                break

        if matched_endpoint:
            # Счётчик всех запросов по персональным эндпоинтам
            person_requests_total.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).inc()

            # Засекаем время выполнения
            person_request_duration_seconds.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).observe(info.modified_duration)

            # Счётчик 5xx ошибок, если есть
            if 500 <= info.response.status_code < 600:
                person_5xx_errors_total.labels(
                    endpoint=matched_endpoint,
                    method=info.request.method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation


def instrument_film_endpoints() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        film_endpoint_patterns = {
            "/films/popular": re.compile(r"^/api/v1/films/$"),  # Популярные фильмы
            "/films/search": re.compile(r"^/api/v1/films/search$"),  # Поиск фильмов
            "/films/{film_uuid}": re.compile(
                r"^/api/v1/films/[^/]+$"
            ),  # Полная информация по фильму
        }

        if info.request.method not in ["GET"]:
            return

        matched_endpoint = None

        for endpoint, pattern in film_endpoint_patterns.items():
            if pattern.match(info.request.url.path):
                matched_endpoint = endpoint
                break

        if matched_endpoint:
            # Считаем общее количество запросов
            film_requests_total.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).inc()

            # Засекаем время выполнения
            film_request_duration_seconds.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).observe(info.modified_duration)

            # Считаем ошибки 5xx, если есть
            if 500 <= info.response.status_code < 600:
                film_5xx_errors_total.labels(
                    endpoint=matched_endpoint,
                    method=info.request.method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation
