from script_parser import parser


def test_init():
    p = parser.Parser(['chrome.init id secret ref'])
    p.execute()

    assert p.variables['client_id'] == 'id'
    assert p.variables['client_secret'] == 'secret'
    assert p.variables['refresh_token'] == 'ref'
