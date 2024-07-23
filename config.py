from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()

USERS = [369558396]
INTERVAL = 900
TOKEN = getenv('TOKEN')

KWORK_MAIL = getenv('KWORK_MAIL')
KWORK_PASS = getenv('KWORK_PASS')

# Нужно передать словарь вида {"userId": "", "uad":"", "slrememberme":""}
KWORK_COOKIES = json.loads(getenv('KWORK_COOKIES'))

SKIP_UPDATES = True
LOG_LEVEL = "DEBUG"

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
            "level": LOG_LEVEL,
            "formatter": "default"
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "default",
            "filename": "main.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "UTF-8"
        }
    },
    "loggers": {
        "default": {
            "handlers": ["console", "rotating_file"],
            "level": LOG_LEVEL
        }
    }
}


if __name__ == '__main__':
    print(KWORK_COOKIES)
    print(type(KWORK_COOKIES))