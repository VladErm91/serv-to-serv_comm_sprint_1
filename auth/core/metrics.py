import re
from typing import Callable

from prometheus_client import Counter
from prometheus_fastapi_instrumentator.metrics import Info

# Общее количество запросов к авторизационным эндпоинтам
auth_requests_total = Counter(
    "auth_requests_total",
    "Total number of auth-related requests",
    ["endpoint", "method"],
)

# Счётчик всех ошибок 5xx для авторизационных эндпоинтов
auth_5xx_errors_total = Counter(
    "auth_5xx_errors_total",
    "Total number of 5xx errors for auth endpoints",
    ["endpoint", "method", "status_code"],
)

# Общее количество запросов к пользовательским эндпоинтам
user_requests_total = Counter(
    "user_requests_total",
    "Total number of user-related requests",
    ["endpoint", "method"],
)

# Счётчик всех ошибок 5xx для пользовательских эндпоинтов
user_5xx_errors_total = Counter(
    "user_5xx_errors_total",
    "Total number of 5xx errors for user endpoints",
    ["endpoint", "method", "status_code"],
)


def instrument_auth_endpoints() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        auth_endpoints = [
            "/login",
            "/refresh-token",
            "/social/login",
        ]

        if info.request.method in ["POST", "GET"] and any(
            info.request.url.path.startswith(ep) for ep in auth_endpoints
        ):
            endpoint = info.request.url.path
            method = info.request.method

            # Увеличиваем счётчик общего числа запросов
            auth_requests_total.labels(endpoint=endpoint, method=method).inc()

            # Если статус-код 5xx — увеличиваем отдельный счётчик
            if 500 <= info.response.status_code < 600:
                auth_5xx_errors_total.labels(
                    endpoint=endpoint,
                    method=method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation


def instrument_user_endpoints() -> Callable[[Info], None]:
    def instrumentation(info: Info) -> None:
        # Список эндпоинтов
        user_endpoint_patterns = {
            "/register": re.compile(r"^/register$"),
            "/change-password": re.compile(r"^/change-password$"),
            "/users/{user_id}": re.compile(r"^/users/[^/]+$"),
        }

        if info.request.method not in ["GET", "POST", "PATCH", "DELETE"]:
            return

        matched_endpoint = None
        for endpoint, pattern in user_endpoint_patterns.items():
            if pattern.match(info.request.url.path):
                matched_endpoint = endpoint
                break

        if matched_endpoint:
            user_requests_total.labels(
                endpoint=matched_endpoint, method=info.request.method
            ).inc()

            if 500 <= info.response.status_code < 600:
                user_5xx_errors_total.labels(
                    endpoint=matched_endpoint,
                    method=info.request.method,
                    status_code=str(info.response.status_code),
                ).inc()

    return instrumentation
