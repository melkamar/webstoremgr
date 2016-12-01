import logging
import os

# log_formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
log_formatter = logging.Formatter(
    "%(asctime)s [%(filename)-15.15s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

loggers = []


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

    log_filename = os.path.join(os.getcwd(), "{}.log".format(os.path.basename(name)))
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    loggers.append(logger)
    return logger
