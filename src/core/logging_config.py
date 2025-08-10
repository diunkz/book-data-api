import logging.config
import os

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logging():
    """Configura o sistema de logging para o projeto."""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": os.path.join(LOGS_DIR, "book_data_api.log"),
                "maxBytes": 1024 * 1024 * 5,
                "backupCount": 3,
                "encoding": "utf-8",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "httpx": {
                "level": "WARNING",
                "propagate": False,
            },
            "httpcore": {
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    }
    logging.config.dictConfig(config)
