import os
import json
import logging
import logging.config

FOLDER_LOG = 'logs'
LOGGING_CONFIG_FILE = 'logs/loggers.json'


def create_log_folder():
    if not os.path.exists(FOLDER_LOG):
        os.mkdir(FOLDER_LOG)
    if not os.path.exists(LOGGING_CONFIG_FILE):
        with open(LOGGING_CONFIG_FILE, 'w') as file:
            pass


def getLogger(name, template='default'):
    create_log_folder()
    try:
        with open(LOGGING_CONFIG_FILE, "r") as f:
            dict_config = json.load(f)
            dict_config["loggers"][name] = dict_config["loggers"][template]
        logging.config.dictConfig(dict_config)
    except FileNotFoundError:
        pass
    finally:
        return logging.getLogger(name)

main_logger = getLogger('"uvicorn.access"')

if __name__ == '__main__':
    logger = getLogger('__main__')