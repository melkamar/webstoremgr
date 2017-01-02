import requests
import pytest
import json
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
