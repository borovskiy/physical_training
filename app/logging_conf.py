import logging
import contextvars
from logging.config import dictConfig

from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent
_LOG_FILE = str((_LOG_DIR / "app.log"))

request_id_var = contextvars.ContextVar("request_id", default="")
request_user_var = contextvars.ContextVar("request_user", default="")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.process_id = getattr(record, "process_id", request_id_var.get())
        if not hasattr(record, "route"):
            record.route = ""
        if not hasattr(record, "method"):
            record.method = ""
        if not hasattr(record, "user"):
            record.user = request_user_var.get()
        if not hasattr(record, "component"):
            record.component = ""
        if not hasattr(record, "payload"):
            record.payload = ""
        return True


LOG_FORMAT = "%(asctime)s %(levelname)s [%(process_id)s] [%(method)s] [%(route)s] [user:%(user)s] [%(component)s] %(message)s %(payload)s"
ACCESS_FORMAT = "%(asctime)s %(levelname)s [%(process_id)s] — %(message)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation": {"()": "logging_conf.CorrelationIdFilter"}
    },
    "formatters": {
        "default": {"format": LOG_FORMAT},
        "access": {"format": ACCESS_FORMAT},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["correlation"],
            "formatter": "default",
        },
        "uvicorn_access_console": {
            "class": "logging.StreamHandler",
            "filters": ["correlation"],
            "formatter": "access",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": _LOG_FILE,
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "delay": True,
            "filters": ["correlation"],
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn_access_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
