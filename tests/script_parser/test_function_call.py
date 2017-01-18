from flexmock import flexmock

from script_parser import parser


def test_call_function():
    """ Test that function name is parsed and called correctly. """
    foo_obj = flexmock()
    foo_obj.should_receive('foo_func').with_args('a', 'b', 'c').once()
    foo_obj.should_receive('foo_func2').with_args('x', 'y').twice()
    foo_obj.should_receive('foo_funca').never()  # check that no other function is called

    p = parser.Parser(['foo.func a b c',
                       'foo.func2 x y',
                       'foo.func2 x y'])

    p.functions['foo.func'] = foo_obj.foo_func
    p.functions['foo.func2'] = foo_obj.foo_func2

    p.execute()
