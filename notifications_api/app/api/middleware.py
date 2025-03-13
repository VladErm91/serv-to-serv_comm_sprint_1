# app/api/middleware.py
import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"Error creating notification: {e}")
            return JSONResponse(
                status_code=500,
                content={"error: Internal Server Error, detail": str(e)},
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.debug(
            "method = %(method)s, path = %(path)s completed in time = %(process_time)d with status code = %(status_code)d",
            {
                "method": request.method,
                "path": request.url.path,
                "process_time": process_time,
                "code": response.status_code,
            },
        )
        return response


def setup_middleware(app: FastAPI) -> None:
    """Настройка middleware для приложения."""
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
