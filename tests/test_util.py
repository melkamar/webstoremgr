import requests
import pytest
import json
import os
import zipfile

from flexmock import flexmock
import webstore_manager.util as util
from webstore_manager.util import pushd, temp_dir


def test_check_requests_response_status_ok():
    response = flexmock()
    response.should_receive('raise_for_status').and_return(True)

    util.handle_requests_response_status(response)


def test_check_requests_response_status_fail():
    response = flexmock()
    response.should_receive('raise_for_status').and_raise(requests.HTTPError)
    response.should_receive('json').and_return(json.dumps({"foo": "bar"}))

    with pytest.raises(requests.HTTPError):
        util.handle_requests_response_status(response)


def test_read_json_key_ok():
    assert util.read_json_key({"foo": "bar"}, "foo") == "bar"


def test_read_json_key_fail():
    with pytest.raises(KeyError):
        util.read_json_key({"foo": "bar"}, "invalid")


def test_makezip_nodest():
    zip_path = os.path.join(os.getcwd(), 'tests/files/sample_folder')
    temp_path = 'tests/files/temp_test_makezip'
    zip_name = 'testzip.zip'

    with temp_dir(temp_path):
        with pushd(temp_path):
            assert not os.path.exists(zip_name)
            util.make_zip(zip_name, zip_path)
            assert os.path.exists(zip_name)

            archive = zipfile.ZipFile(zip_name, 'r')
            txt = archive.read('hello').decode("utf-8")
            assert txt.startswith('Sample bare content')
            archive.close()

            os.remove(zip_name)
            assert not os.path.exists(zip_name)


def test_makezip_dest():
    zip_path = os.path.join(os.getcwd(), 'tests/files/sample_folder')
    temp_path = 'tests/files/temp_test_makezip'
    zip_name = 'testzip.zip'

    with temp_dir(temp_path):
        assert not os.path.exists(zip_name)
        assert not os.path.exists(os.path.join(temp_path, zip_name))
        util.make_zip(zip_name, zip_path, dest_dir=temp_path)
        assert os.path.exists(os.path.join(temp_path, zip_name))

        archive = zipfile.ZipFile(os.path.join(temp_path, zip_name), 'r')
        txt = archive.read('hello').decode("utf-8")
        assert txt.startswith('Sample bare content')
        archive.close()

        os.remove(os.path.join(temp_path, zip_name))
        assert not os.path.exists(os.path.join(temp_path, zip_name))


def test_unzip():
    unzip_path = 'tests/files/temp_test_unzip'
    with temp_dir(unzip_path):
        assert not os.path.exists(os.path.join(unzip_path, 'hello'))
        util.unzip('tests/files/sample_zip.zip', unzip_path)

        assert os.path.exists(os.path.join(unzip_path, 'hello'))
        with open(os.path.join(unzip_path, 'hello')) as f:
            txt = f.read()
            assert txt.startswith('Sample content of zip')
