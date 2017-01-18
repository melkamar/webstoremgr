import os
import pytest
from script_parser import parser


def test_pushd_popd():
    p = parser.Parser("foo")
    startdir = os.getcwd()

    p.execute_line("pushd tests")
    assert os.getcwd() == os.path.join(startdir, 'tests')

    p.execute_line("pushd files")
    assert os.getcwd() == os.path.join(startdir, 'tests', 'files')

    p.execute_line("popd")
    assert os.getcwd() == os.path.join(startdir, 'tests')

    p.execute_line("popd")
    assert os.getcwd() == startdir


def test_popd_empty():
    p = parser.Parser("foo")
    startdir = os.getcwd()

    p.execute_line("pushd tests")
    assert os.getcwd() == os.path.join(startdir, 'tests')

    p.execute_line("popd")
    with pytest.raises(IndexError):
        p.execute_line("popd")


def test_cd():
    p = parser.Parser("foo")
    startdir = os.getcwd()

    p.execute_line("cd tests")
    assert os.getcwd() == os.path.join(startdir, 'tests')
