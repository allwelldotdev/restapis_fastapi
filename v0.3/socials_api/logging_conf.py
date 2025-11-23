import logging
import time
from logging.config import dictConfig

from socials_api.config import DevConfig, config

# convert time to UTC aware
logging.Formatter.converter = time.gmtime


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                    "format": "%(asctime)s | %(levelname)-7s | %(name)s:%(module)s:%(lineno)d - %(message)s",
                },
                "json": {  # Optional: for structured logging
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                    "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",  # alt: "rich.logging.RichHandler"
                    "level": "DEBUG",
                    "formatter": "console",
                },
                "rich": {
                    "class": "rich.logging.RichHandler",  # this handler uses "rich.logging.RichHandler"
                    "level": "DEBUG",
                    "formatter": "console",
                },
            },
            "loggers": {
                "socials_api": {
                    "handlers": ["default"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,  # don't send logs to 'root' : what is root? root.socials_api.api.routes.user_post
                },
            },
        }
    )
