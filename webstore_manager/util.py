import atexit
import os
import tempfile
import zipfile
import requests
import shutil
from contextlib import contextmanager

from . import logging_helper

logger = logging_helper.get_logger(__file__)

build_dir = tempfile.mkdtemp()
work_dir = os.getcwd()
# logger.debug("Using temporary directory: {}".format(build_dir))


def make_zip(zip_name, path, dest_dir=None):
    """

    Args:
        zip_name(str): Name of the new zip archive.
        path(str): Root folder of the path to zip.
        dest_dir(str, optional): If set, place the created zip to this directory.

    Returns:
        Name of the created zip archive.
    """

    if dest_dir:
        zip_name = os.path.join(dest_dir, zip_name)

    logger.info("Creating zipfile {}".format(zip_name))
    zip_handle = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

    orig_cwd = os.getcwd()

    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            zip_handle.write(os.path.join(root, file))

    os.chdir(orig_cwd)
    return zip_name


def clean():
    # logger.debug("Cleaning temporary directory: {}".format(build_dir))
    # shutil.rmtree(build_dir, ignore_errors=True)
    pass


def handle_requests_response_status(response: requests.Response):
    """
    Check if requests HTTP response is an error. If yes, log this error and pass the exception along.

    Args:
        response(requests.Response): Response object to test for errors.

    Returns:
        None.

    Raises:
        requests.HTTPError
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        logger.error(error)
        logger.error("Response: {}".format(response.json()))
        raise error


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
        return dictionary[key]
    except KeyError as error:
        logger.error("Key '{}' not found in JSON.".format(key))
        if error_message:
            logger.error(error_message)
        logger.error("JSON: {}".format(dictionary))
        logger.error(error)
        raise error


def custom_options(option_list):
    """
    Decorator for Click. Add options in the list to the command.
    Args:
        option_list(:obj:`list` of :obj:`click.option`): list of options

    Returns:
        function
    """

    def ret_func(func):
        for option in reversed(option_list):
            func = option(func)
        return func

    return ret_func


def unzip(filename, dest_dir):
    """
    Unzip a file into the given folder. Contents of the folder will be erased if it exists. If it does not exist, it
     will be created.

    Args:
        filename(str): Name of the file to unzip.
        dest_dir(str): Destination folder to which contents of the zipfile will be added.

    Returns:

    """
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)

    zip_file = zipfile.ZipFile(filename)
    logger.debug("Extracting {} to path {}".format(filename, dest_dir))
    zip_file.extractall(dest_dir)
    zip_file.close()


@contextmanager
def pushd(directory):
    """
    Context managed function simulating pushd-popd bash builtins.

    Use::

       with pushd(directory):
           pass

    Args:
        directory(str): Directory to pushd into.

    Returns:
        None
    """

    prev_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_dir)


@contextmanager
def temp_dir(directory):
    """
    Create an empty directory (or clean it if exists) for the span of the context.

    Use::

       with temp_dir(directory):
           pass

    Args:
        directory(str): Directory to create.

    Returns:
        None
    """

    shutil.rmtree(directory, ignore_errors=True)
    os.makedirs(directory)
    yield
    shutil.rmtree(directory, ignore_errors=True)


atexit.register(clean)
