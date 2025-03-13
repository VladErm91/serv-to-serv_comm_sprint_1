import re
from typing import Callable

from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator.metrics import Info

# Метрики для эндпоинтов лайков
likes_requests_total = Counter(
    "likes_requests_total",
    "Total number of like-related requests",
    ["endpoint", "method"],
)

likes_errors_total = Counter(
    "likes_errors_total",
    "Total number of errors in like endpoints",
    ["endpoint", "method", "error_type"],
)

likes_request_duration_seconds = Histogram(
    "likes_request_duration_seconds",
    "Duration of like requests",
    ["endpoint", "method"],
)

# Метрики для эндпоинтов отзывов
review_requests_total = Counter(
    "review_requests_total",
    "Total number of review-related requests",
    ["endpoint", "method"],
)
review_request_duration_seconds = Histogram(
    "review_request_duration_seconds",
    "Duration of review-related requests",
    ["endpoint", "method"],
)
review_5xx_errors_total = Counter(
    "review_5xx_errors_total",
    "Total number of 5xx errors for review endpoints",
    ["endpoint", "method", "status_code"],
)


# Метрики для эндпоинтов закладок
bookmark_requests_total = Counter(
    "bookmark_requests_total",
    "Total number of bookmark-related requests",
    ["endpoint", "method"],
)
bookmark_request_duration_seconds = Histogram(
    "bookmark_request_duration_seconds",
    "Duration of bookmark-related requests",
    ["endpoint", "method"],
)
bookmark_5xx_errors_total = Counter(
    "bookmark_5xx_errors_total",
    "Total number of 5xx errors for bookmark endpoints",
    ["endpoint", "method", "status_code"],
)


def instrument_likes() -> Callable[[Info], None]:
    """Функция-инструментатор для метрик эндпоинтов лайков"""

    def instrumentation(info: Info) -> None:
        if info.request.method not in ["GET", "POST"]:
            return  # Игнорируем ненужные методы

        # Определяем, относится ли запрос к лайкам
        if "/movies" in info.request.url.path and (
            "/likes/" in info.request.url.path
            or "/average_rating/" in info.request.url.path
        ):
            endpoint = info.request.url.path
            method = info.request.method

            likes_requests_total.labels(endpoint=endpoint, method=method).inc()

            if info.response.status_code >= 500:
                likes_errors_total.labels(
                    endpoint=endpoint,
                    method=method,
                    error_type=str(info.response.status_code),
                ).inc()

            # Засекаем время выполнения запроса
            likes_request_duration_seconds.labels(
                endpoint=endpoint, method=method
            ).observe(info.modified_duration)

    return instrumentation


def instrument_reviews() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        review_endpoint_patterns = {
            "/reviews/create": r"^/reviews/$",
            "/reviews/{review_id}/like": r"^/reviews/[^/]+/like/$",
            "/reviews/{review_id}/dislike": r"^/reviews/[^/]+/dislike/$",
            "/movies/{movie_id}/reviews": r"^/movies/[^/]+/reviews/$",
        }

        if info.request.method not in ["GET", "POST"]:
            return

        matched_endpoint = None
        for endpoint, pattern in review_endpoint_patterns.items():
            if re.match(pattern, info.request.url.path):
                matched_endpoint = endpoint
                break

        if matched_endpoint:
            # Количество запросов
            review_requests_total.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).inc()

            # Засекаем время выполнения
            review_request_duration_seconds.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).observe(info.modified_duration)

            # Ошибки 5xx
            if 500 <= info.response.status_code < 600:
                review_5xx_errors_total.labels(
                    endpoint=matched_endpoint,
                    method=info.request.method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation


def instrument_bookmarks() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        bookmark_endpoint_patterns = {
            "/bookmarks/create": r"^/bookmarks/$",
            "/users/{user_id}/bookmarks": r"^/users/[^/]+/bookmarks/$",
        }

        if info.request.method not in ["GET", "POST"]:
            return

        matched_endpoint = None
        for endpoint, pattern in bookmark_endpoint_patterns.items():
            if re.match(pattern, info.request.url.path):
                matched_endpoint = endpoint
                break

        if matched_endpoint:
            # Количество запросов
            bookmark_requests_total.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).inc()

            # Засекаем время выполнения
            bookmark_request_duration_seconds.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).observe(info.modified_duration)

            # Ошибки 5xx
            if 500 <= info.response.status_code < 600:
                bookmark_5xx_errors_total.labels(
                    endpoint=matched_endpoint,
                    method=info.request.method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation
