import atexit
import os
import shutil
import tempfile
import zipfile

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
    logger.debug("Cleaning temporary directory: {}".format(build_dir))
    shutil.rmtree(build_dir, ignore_errors=True)


atexit.register(clean)
