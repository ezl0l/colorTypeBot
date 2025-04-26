import logging

from logging.handlers import RotatingFileHandler
import os.path


def setup_logging():
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s %(message)s')

    file_debug_handler = RotatingFileHandler('logs/debug.log',
                                             mode='a',
                                             maxBytes=10 * 1024 * 1024,
                                             backupCount=3,
                                             encoding='utf-8')
    file_debug_handler.setLevel(logging.DEBUG)
    file_debug_handler.setFormatter(formatter)

    file_error_handler = RotatingFileHandler('logs/error.log',
                                             mode='a',
                                             maxBytes=20 * 1024 * 1024,
                                             backupCount=3,
                                             encoding='utf-8')
    file_error_handler.setLevel(logging.ERROR)
    file_error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_error_handler)
    logger.addHandler(file_debug_handler)
    logger.addHandler(console_handler)
