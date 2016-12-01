import logging
import os

import appdirs

# log_formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
log_formatter = logging.Formatter(
    "%(asctime)s [%(filename)-15.15s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

loggers = []

log_dir = appdirs.user_log_dir("webstore_deployer", "melkamar")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "log")


def init_logging():
    logging.basicConfig(level=logging.INFO)

    # Set logging format for requests
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARN)
    requests_log.propagate = False
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    requests_log.addHandler(console_handler)


init_logging()


def set_level(level):
    for logger in loggers:
        logger.setLevel(level)


def get_logger(name):
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
