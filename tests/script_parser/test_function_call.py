from flexmock import flexmock

from webstore_manager.script_parser import parser


def test_call_function():
    """ Test that function name is parsed and called correctly. """
    p = parser.Parser(['foo.func a b c',
                       'foo.func2 x y',
                       'foo.func2 x y'])

    foo_obj = flexmock()
    foo_obj.should_receive('foo_func').with_args(p, 'a', 'b', 'c').once()
    foo_obj.should_receive('foo_func2').with_args(p, 'x', 'y').twice()
    foo_obj.should_receive('foo_funca').never()  # check that no other function is called

    p.functions['foo.func'] = foo_obj.foo_func
    p.functions['foo.func2'] = foo_obj.foo_func2

    p.execute()
