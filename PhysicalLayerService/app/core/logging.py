import logging
import os
from logging.config import dictConfig

from app.core.config import get_settings


def _level_from_env(default_level: str) -> str:
    return os.getenv("LOG_LEVEL", default_level).upper()


def configure_logging() -> None:
    """
    Configure structured logging for the service using dictConfig.
    Safe to call multiple times.
    """
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
                "uvicorn": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": _level_from_env(settings.LOG_LEVEL),
                }
            },
            "loggers": {
                "uvicorn": {"handlers": ["console"], "level": _level_from_env(settings.LOG_LEVEL), "propagate": False},
                "uvicorn.error": {"handlers": ["console"], "level": _level_from_env(settings.LOG_LEVEL), "propagate": False},
                "uvicorn.access": {"handlers": ["console"], "level": _level_from_env(settings.LOG_LEVEL), "propagate": False},
                "app": {"handlers": ["console"], "level": _level_from_env(settings.LOG_LEVEL), "propagate": False},
            },
            "root": {"level": _level_from_env(settings.LOG_LEVEL), "handlers": ["console"]},
        }
    )
