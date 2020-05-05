import os
from eon_backend.settings.common.base import BASE_DIR
from utils.logger import Logging

OUT_DIR = os.path.join(BASE_DIR, "logs/core")

if not os.path.exists(OUT_DIR):
    os.mkdir(BASE_DIR + '/logs')
    os.mkdir(BASE_DIR + '/logs/core')

CORE_APP_LOG_DIR = (
    os.environ.get("EON_LOG_DIR") if os.environ.get("EON_LOG_DIR") else OUT_DIR
)
# loggers
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'console': {
            'format': '[%(levelname)s : %(asctime)s]  %(funcName)s  %(lineno)d  %(message)s'
        },
        'file': {
            'format': '[%(levelname)s : %(asctime)s]  %(funcName)s  %(lineno)d  %(message)s'
        }
    },
    "handlers": {
        "debug": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(CORE_APP_LOG_DIR, "debug.log"),
            "formatter": 'file',
        },
        "info": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(CORE_APP_LOG_DIR, "info.log"),
            "formatter": 'file',
        },
        "error": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(CORE_APP_LOG_DIR, "error.log"),
            "formatter": 'file',
        },
        "warning": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": os.path.join(CORE_APP_LOG_DIR, "warning.log"),
            "formatter": 'file',
        }
    },
    "loggers": {
        "debug_logger": {"handlers": ["debug"], "level": "DEBUG", "propagate": True},
        "info_logger": {"handlers": ["info"], "level": "INFO", "propagate": True},
        "error_logger": {"handlers": ["error"], "level": "ERROR", "propagate": True},
        "warning_logger": {"handlers": ["warning"], "level": "WARNING", "propagate": True}
    },
}
LOGGER_SERVICE = Logging()