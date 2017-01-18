from script_parser import parser
import os


def test_environ_init():
    """ Set up variables in environment and check parser uses them to init properly. """

    os.environ['client_id'] = 'x'
    os.environ['client_secret'] = 'y'
    os.environ['refresh_token'] = 'z'

    p = parser.Parser(['chrome.init ${env.client_id} ${env.client_secret} ${env.refresh_token}'])
    p.execute()

    assert p.variables['client_id'] == 'x'
    assert p.variables['client_secret'] == 'y'
    assert p.variables['refresh_token'] == 'z'
