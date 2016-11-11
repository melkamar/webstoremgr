import logging


def init_logging():
    logging.basicConfig(format="%(asctime)s: %(levelname)s: %(message)s",
                        level=logging.DEBUG,
                        filename="webstore-deployer.log")


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.StreamHandler())
    return logger
