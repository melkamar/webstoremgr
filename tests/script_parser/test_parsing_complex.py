import os

from flexmock import flexmock

from webstore_manager.script_parser import parser


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


def test_multiple_commands():
    """ Advanced scenario. Set environment, assign environment to local vars, use those to call several functions. """

    cli = 'cli'
    sec = 'sec'
    ref = 'ref'
    app = 'app'

    os.environ['clientid'] = cli
    os.environ['secret'] = sec
    os.environ['reftoken'] = ref

    script = ['id = ${env.clientid}',
              'secret = ${env.secret}',
              'ref = ${env.reftoken}',
              'chrome.init ${id} ${secret} ${ref}',
              'chrome.setapp {}'.format(app), ]

    p = parser.Parser(script=script)

    foo_obj = flexmock()
    foo_obj.should_receive('chromeinit').with_args(p, cli, sec, ref).once()
    foo_obj.should_receive('chromesetapp').with_args(p, app).once()

    p.functions['chrome.init'] = foo_obj.chromeinit
    p.functions['chrome.setapp'] = foo_obj.chromesetapp

    p.execute()
