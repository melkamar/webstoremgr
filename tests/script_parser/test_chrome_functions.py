import os
import shutil

import pytest
from flexmock import flexmock

from webstore_manager.chrome_store.chrome_store import ChromeStore
from webstore_manager.script_parser import parser


def test_init():
    p = parser.Parser(['chrome.init id secret ref'])
    p.execute()

    assert p.variables['client_id'] == 'id'
    assert p.variables['client_secret'] == 'secret'
    assert p.variables['refresh_token'] == 'ref'


def test_setapp():
    p = parser.Parser(['chrome.init id secret ref'])
    p.execute()
    with pytest.raises(KeyError):
        assert not p.variables['app_id']

    p.execute_line('chrome.setapp appid')
    assert p.variables['app_id'] == 'appid'
    assert p.variables['chrome_store'].app_id == 'appid'


def test_new():
    """ Test if chrome store's upload/new function is called as expected (after its initialization). """
    p = parser.Parser('foo')

    p.execute_line('chrome.init id secret ref')
    mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
    mock_store.should_receive('upload').with_args('fn', True).once()
    p.variables['chrome_store'] = mock_store

    p.execute_line('chrome.new fn')


def test_new_no_init():
    p = parser.Parser(['chrome.new fn'])

    with pytest.raises(parser.InvalidStateException):
        p.execute()


def test_upload():
    """ Test if chrome store's upload/update function is called as expected (after its initialization). """
    p = parser.Parser('foo')

    p.execute_line('chrome.init id secret ref')
    mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
    mock_store.should_receive('upload').with_args('fn', False).once()
    p.variables['chrome_store'] = mock_store

    p.execute_line('chrome.update fn')


def test_upload_no_init():
    p = parser.Parser(['chrome.update fn'])

    with pytest.raises(parser.InvalidStateException):
        p.execute()


@pytest.mark.parametrize(
    ["txt", "target"],
    [("public", ChromeStore.TARGET_PUBLIC),
     ("trusted", ChromeStore.TARGET_TRUSTED)])
def test_publish(txt, target):
    """ Test if chrome store's publish function is called as expected. """
    p = parser.Parser('foo')

    p.execute_line('chrome.init id secret ref')
    mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
    mock_store.should_receive('publish').with_args(target).once()
    p.variables['chrome_store'] = mock_store

    p.execute_line('chrome.publish {}'.format(txt))


def test_publish_incorrect_tgt():
    p = parser.Parser('foo')

    p.execute_line('chrome.init id secret ref')

    with pytest.raises(ValueError):
        p.execute_line('chrome.publish abc')


def test_publish_no_init():
    p = parser.Parser(['chrome.publish trusted'])

    with pytest.raises(parser.InvalidStateException):
        p.execute()


def test_check_version():
    p = parser.Parser('foo')
    p.execute_line('chrome.init id secret ref')
    p.execute_line('chrome.setapp appid')

    mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
    mock_store.should_receive('get_uploaded_version').with_args().and_return('1.0.12345').once()
    p.variables['chrome_store'] = mock_store

    p.execute_line('chrome.check_version 1.0.12345')


def test_unpack():
    zip_fn = 'tests/files/sample_zip.zip'
    target_dir = 'tests/files/tempfolder'

    p = parser.Parser('foo')
    p.execute_line('chrome.unpack {} {}'.format(zip_fn, target_dir))

    assert os.path.exists(zip_fn)

    with open(os.path.join(target_dir, 'hello')) as f:
        assert f.read().find("Sample content of zip") != -1  # Make sure expected content is present in archive

    shutil.rmtree(target_dir)


# def test_check_version_incorrect():
#     p = parser.Parser('foo')
#     p.execute_line('chrome.init id secret ref')
#     p.execute_line('chrome.setapp appid')
#
#     mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
#     mock_store.should_receive('get_uploaded_version').with_args().and_return('2.0.12345').at_most().twice()
#     p.variables['chrome_store'] = mock_store
#
#     with pytest.raises(ValueError):
#         p.execute_line('chrome.check_version 1.0.12345 1')
#
#
# def test_check_version_incorrect_longer_timeout():
#     p = parser.Parser('foo')
#     p.execute_line('chrome.init id secret ref')
#     p.execute_line('chrome.setapp appid')
#
#     mock_store = flexmock(p.variables['chrome_store'])  # Mock the store, do not actually send anything
#     mock_store.should_receive('get_uploaded_version').with_args().and_return('2.0.12345').at_least().times(3)
#     p.variables['chrome_store'] = mock_store
#
#     with pytest.raises(ValueError):
#         p.execute_line('chrome.check_version 1.0.12345 15')
