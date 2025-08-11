import logging.config
import os

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

BASE_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple_console": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple_console",
            "level": "INFO",
        },
    },
    "loggers": {
        "httpx": {"level": "WARNING", "propagate": False},
        "httpcore": {"level": "WARNING", "propagate": False},
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}


def setup_pipeline_logging():
    """Configura o logging para os scripts de ingestão de dados."""
    config = BASE_CONFIG.copy()
    config["handlers"]["pipeline_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "default",
        "filename": os.path.join(LOGS_DIR, "ingestion.log"),
        "maxBytes": 1024 * 1024 * 5,
        "backupCount": 3,
        "encoding": "utf-8",
        "level": "DEBUG",
    }
    config["root"]["handlers"].append("pipeline_file")
    logging.config.dictConfig(config)


def setup_api_logging():
    """Configura o logging para a aplicação FastAPI."""
    config = BASE_CONFIG.copy()
    config["handlers"]["api_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "default",
        "filename": os.path.join(LOGS_DIR, "api.log"),
        "maxBytes": 1024 * 1024 * 5,
        "backupCount": 3,
        "encoding": "utf-8",
        "level": "DEBUG",
    }
    config["loggers"]["uvicorn.access"] = {
        "handlers": ["api_file", "console"],
        "level": "INFO",
        "propagate": False,
    }
    config["loggers"]["uvicorn.error"] = {
        "handlers": ["api_file", "console"],
        "level": "INFO",
        "propagate": False,
    }
    config["root"]["handlers"].append("api_file")
    logging.config.dictConfig(config)
