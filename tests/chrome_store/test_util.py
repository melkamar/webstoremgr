import requests
import pytest
import json
import os
import shutil
from flexmock import flexmock
import webstore_deployer.util as util


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


def test_unzip():
    unzip_path = os.path.join('tests', 'files', 'temp_test_unzip')
    shutil.rmtree(unzip_path, ignore_errors=True)
    os.makedirs(unzip_path)

    assert not os.path.exists(os.path.join(unzip_path, 'hello'))
    util.unzip('tests/files/sample_zip.zip', unzip_path)

    assert os.path.exists(os.path.join(unzip_path, 'hello'))
    with open(os.path.join(unzip_path, 'hello')) as f:
        txt = f.read()
        assert txt == 'Sample content of zip \n'

    shutil.rmtree(unzip_path, ignore_errors=True)
