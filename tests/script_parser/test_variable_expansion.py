from webstore_manager.script_parser import parser
import pytest

import os


def test_resolve_variable():
    p = parser.Parser(['foo'])
    p.variables['abc'] = 'hello'
    assert p.resolve_variable("${abc}") == 'hello'


def test_resolve_variable_unset():
    p = parser.Parser(['foo'])
    with pytest.raises(parser.VariableNotDefinedException):
        p.resolve_variable("${xyz}") == 'hello'


def test_resolve_env_variable():
    os.environ['abc'] = 'hello'
    p = parser.Parser(['foo'])
    assert p.resolve_variable("${env.abc}") == 'hello'


def test_resolve_env_variable_unset():
    os.environ['xyz'] = ''
    p = parser.Parser(['foo'])
    assert not p.resolve_variable("${env.xyz}")
