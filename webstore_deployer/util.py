import atexit
import os
import tempfile
import zipfile
import requests

from . import logging_helper

logger = logging_helper.get_logger(__file__)

build_dir = tempfile.mkdtemp()
work_dir = os.getcwd()
logger.debug("Using temporary directory: {}".format(build_dir))


def make_zip(zip_name, path, dest_dir=None):
    if dest_dir:
        zip_name = os.path.join(dest_dir, zip_name)

    logger.info("Creating zipfile {}".format(zip_name))
    zip_handle = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            zip_handle.write(os.path.join(root, file))

    return zip_name


def clean():
    # logger.debug("Cleaning temporary directory: {}".format(build_dir))
    # shutil.rmtree(build_dir, ignore_errors=True)
    pass


def check_requests_response_status(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        logger.error(error)
        logger.error("Response: {}".format(response.json()))
        exit(3)


def read_json_key(dictionary, key, error_message=""):
    """
    Read key in JSON entry. If key not found, display error message and exit.

    Args:
        dictionary: Python dictionary from which to read the key.
        key: Key to read from the dictionary.
        error_message(str, optional): Message to be displayed in case of failure.

    Returns:
        str: Value associated with the key in the dictionary. If no such key found, program will exit.
    """
    try:
        value = dictionary[key]
    except KeyError as error:
        logger.error("Key '{}' not found in JSON.".format(key))
        if error_message:
            logger.error(error_message)
        logger.error("JSON: {}".format(dictionary))
        logger.error(error)
        exit(4)

    return value


atexit.register(clean)
