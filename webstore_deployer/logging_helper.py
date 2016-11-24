import logging

# log_formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")


def init_logging():
    level = logging.DEBUG

    logging.basicConfig(level=level)

    # Set logging format for requests
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARN)
    requests_log.propagate = False
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    requests_log.addHandler(console_handler)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("{}.log".format(name))
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return logger
