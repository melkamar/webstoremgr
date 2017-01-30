import pytest

from webstore_manager.script_parser import parser


@pytest.mark.parametrize(["command", "var", "value"],
                         [
                             ("ab = cd", "ab", "cd"),
                             ("  ab  = cd", "ab", "cd"),
                             (" ab = cd ", "ab", "cd"),
                             ("ab =   c ", "ab", "c"),
                             ("ab   = cd ", "ab", "cd"),
                             ("ab = c.d ", "ab", "c.d"),
                         ])
def test_assignment(command, var, value):
    p = parser.Parser([command])
    p.execute()

    assert p.variables[var] == value


@pytest.mark.parametrize(["command", "var", "value"],
                         [
                             ("ab==cd", "ab", "cd"),
                             ("ab=cd=", "ab", "cd"),
                             ("ab=", "ab", "cd"),
                             ("=ab", "ab", "cd"),
                             ("ab=c d", "ab", "cd"),
                             ("ab=c d", "ab", "cd"),
                             ("a.b=cd", "ab", "cd"),
                             ("ab=cd", "ab", "cd"),
                             ("ab= cd", "ab", "cd"),
                             ("ab =cd", "ab", "cd"),
                         ])
def test_assignment_syntax_err(command, var, value):
    p = parser.Parser([command])

    with pytest.raises(parser.FunctionNotDefinedException):
        p.execute()
