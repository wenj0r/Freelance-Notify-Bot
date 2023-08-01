import os
import json
import logging
import logging.config

from config import LOG_CONFIG

FOLDER_LOG = 'logs'


def create_log_folder():
    if not os.path.exists(FOLDER_LOG):
        os.mkdir(FOLDER_LOG)


def getLogger(name, template='default'):
    create_log_folder()

    dict_config = LOG_CONFIG
    dict_config["loggers"][name] = dict_config["loggers"][template]
    logging.config.dictConfig(dict_config)

    return logging.getLogger(name)

main_logger = getLogger('"uvicorn.access"')

if __name__ == '__main__':
    logger = getLogger('__main__')