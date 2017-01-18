import pytest
from flexmock import flexmock
from script_parser import parser
from chrome_store.chrome_store import ChromeStore


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
