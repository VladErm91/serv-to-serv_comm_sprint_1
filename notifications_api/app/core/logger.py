import logging
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from core.config import settings


def setup_logging() -> None:
    """Настройка логирования для приложения."""

    # Создаем директорию для логов, если она не существует
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": settings.log_date_format,
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": """
                    asctime: %(asctime)s
                    name: %(name)s
                    levelname: %(levelname)s
                    message: %(message)s
                    filename: %(filename)s
                    funcName: %(funcName)s
                    lineno: %(lineno)s
                """,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "level": settings.log_level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "app.log",
                "formatter": "default",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": settings.log_level,
            },
            "json_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "app.json.log",
                "formatter": "json",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": settings.log_level,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "json_file"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file", "json_file"],
                "level": settings.log_level,
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console", "file", "json_file"],
                "level": settings.log_level,
                "propagate": False,
            },
            "app": {  # Логи для приложения
                "handlers": ["console", "file", "json_file"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
    }

    try:
        dictConfig(log_config)
        logging.info("Logging configured successfully")
    except Exception as e:
        logging.error(f"Failed to configure logging: {e}")
        raise
