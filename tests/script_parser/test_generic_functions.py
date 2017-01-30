import os
import pytest
import shutil
import zipfile
from webstore_manager.script_parser import parser


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

    os.chdir(startdir)
    assert os.getcwd() == startdir


def test_zip():
    zip_fn = os.path.join(os.getcwd(), 'testzip.zip')

    shutil.rmtree(zip_fn, ignore_errors=True)
    if os.path.exists(zip_fn):
        os.remove(zip_fn)

    assert not os.path.exists(zip_fn)

    p = parser.Parser("foo")
    p.execute_line("zip tests/files/sample_folder testzip.zip")

    assert os.path.exists(zip_fn)

    archive = zipfile.ZipFile(zip_fn, 'r')
    txt = archive.read('hello').decode("utf-8")
    assert txt.find("Sample bare content") != -1  # Make sure expected content is present in archive
    archive.close()

    os.remove(zip_fn)
