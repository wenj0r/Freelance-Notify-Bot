from dotenv import load_dotenv
from os import getenv

load_dotenv()

USERS = [369558396]
INTERVAL = 60
TOKEN = getenv('TOKEN')
SKIP_UPDATES = True

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s: %(levelname)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default"
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "logs/main.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "UTF-8"
        }
    },
    "loggers": {
        "default": {
            "handlers": ["console", "rotating_file"],
            "level": "DEBUG"
        }
    }
}