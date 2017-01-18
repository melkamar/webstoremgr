import pytest
from flexmock import flexmock
from script_parser import parser


def test_init():
    p = parser.Parser(['chrome.init id secret ref'])
    p.execute()

    assert p.variables['client_id'] == 'id'
    assert p.variables['client_secret'] == 'secret'
    assert p.variables['refresh_token'] == 'ref'


def test_new():
    """ Test if chrome store's upload function is called as expected (after its initialization). """
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
