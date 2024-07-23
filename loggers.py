import os
import json
import logging
import logging.config

from config import LOG_CONFIG


def getLogger(name, template='default'):
    dict_config = LOG_CONFIG
    dict_config["loggers"][name] = dict_config["loggers"][template]
    logging.config.dictConfig(dict_config)

    return logging.getLogger(name)

main_logger = getLogger("uvicorn.access")

if __name__ == '__main__':
    logger = getLogger('__main__')