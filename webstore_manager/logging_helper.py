import logging
import os

import appdirs

log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] [%(lineno)-4s] [%(filename)-15.15s] %(message)s")

loggers = []

log_dir = appdirs.user_log_dir("webstore_manager", "melkamar")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "log")


def init_logging():
    """ Initialize app-wide logging. """
    logging.basicConfig(level=logging.DEBUG)

    # Set logging format for requests
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARN)
    requests_log.propagate = False
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    requests_log.addHandler(console_handler)


init_logging()


def set_level(level):
    """ Set new logging level for all created loggers. """
    for logger in loggers:
        logger.setLevel(level)


def get_logger(name):
    """
    Create a new logger with a given name, set its output file and add it to a list of all current loggers.

    Args:
        name: Name of the logger. Usually __file__.

    Returns:
        Newly created logger.
    """
    logger = logging.getLogger(name)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    loggers.append(logger)
    return logger
