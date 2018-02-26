import os
import shutil
import zipfile

import pytest

from webstore_manager.chrome_store.chrome_store import ChromeStore
from webstore_manager.chrome_store.chrome_store import repack_crx
from webstore_manager.constants import ErrorCodes


def test_redeem_code(betamax_session, auth):
    store = ChromeStore(auth['client_id'], auth['client_secret'], session=betamax_session)
    assert store.refresh_token is None

    store.authenticate(auth['code'])
    print("refresh_token: {}".format(store.refresh_token))
    assert store.refresh_token is not None


def test_gen_access_token(betamax_session, auth):
    store = ChromeStore(auth['client_id'],
                        auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        session=betamax_session)

    assert store.generate_access_token() is not None


def test_upload(betamax_session, auth):
    store = ChromeStore(client_id=auth['client_id'],
                        client_secret=auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        app_id=auth['app_id'],
                        session=betamax_session)

    store.upload('tests/files/sample_zip.zip')


def test_upload_app_not_exists(betamax_session, auth):
    """ Upload a new version of a non-existing extension. Expect program to exit. """
    store = ChromeStore(client_id=auth['client_id'],
                        client_secret=auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        app_id=auth['app_id'] + "X",
                        session=betamax_session)

    with pytest.raises(SystemExit) as err:
        store.upload('tests/files/sample_zip.zip')

    assert err.value.code == ErrorCodes.chrome_upload_app_not_found


def test_upload_new_item(betamax_session, auth):
    store = ChromeStore(client_id=auth['client_id'],
                        client_secret=auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        app_id=auth['app_id'],
                        session=betamax_session)

    app_id = store.upload('tests/files/sample_zip.zip', new_item=True)
    assert app_id
    assert app_id == store.app_id
    assert app_id != auth['app_id']


def test_publish(betamax_session, auth):
    store = ChromeStore(client_id=auth['client_id'],
                        client_secret=auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        app_id=auth['app_id'],
                        session=betamax_session)

    app_id = store.publish(ChromeStore.TARGET_TRUSTED)
    assert app_id
    assert app_id == store.app_id
    assert app_id == auth['app_id']


def test_check_status(betamax_session, auth):
    store = ChromeStore(client_id=auth['client_id'],
                        client_secret=auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        app_id=auth['app_id'],
                        session=betamax_session)

    version = store.get_uploaded_version()
    assert version == '1.0.12346'


def test_repack_crx():
    files_dir = os.path.join('tests', 'files')
    fn = os.path.join(files_dir, 'sample_crx.crx')
    tmp_dir = os.path.join(files_dir, 'temp')
    created_fn = os.path.join(tmp_dir, 'sample_crx.zip')

    assert os.path.exists(fn) is True

    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.mkdir(tmp_dir)

    assert os.path.exists(tmp_dir) is True

    assert os.path.exists(created_fn) is False  # No zipfile is present before repacking
    repack_crx(fn, 'tests/files/temp')
    assert os.path.exists(created_fn) is True  # A zipfile was created

    archive = zipfile.ZipFile(created_fn, 'r')

    txt = archive.read('hello').decode("utf-8")
    assert txt.find("Sample content") != -1  # Make sure expected content is present in archive

    txt = archive.read('manifest.json').decode("utf-8")
    assert txt.find('"name": "Melkamar') != -1  # Make sure expected content is present in archive

    archive.close()
    shutil.rmtree(tmp_dir, ignore_errors=True)
