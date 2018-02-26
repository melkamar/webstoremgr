import click

from . import chrome_store
from webstore_manager import logging_helper, util, constants

logger = logging_helper.get_logger(__file__)


@click.group()
def chrome():
    pass


@chrome.command('init', short_help="initialize API key. Run this first.")
@click.argument('client_id', required=True)
def init(client_id):
    print(constants.webstore_init_info.format(client_id))


@chrome.command('auth', short_help="exchange code for auth token. Run this after init.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('code', required=True)
def auth(client_id, client_secret, code):
    access_token, refresh_token = chrome_store.ChromeStore.redeem_code(client_id, client_secret, code)
    print("Received tokens:")
    print("  access_token: {}".format(access_token))
    print("  refresh_token: {}".format(refresh_token))


@chrome.command('gen-token', short_help="generate new access token from refresh token.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('refresh_token', required=True)
def gen_token(client_id, client_secret, refresh_token):
    access_token = chrome_store.ChromeStore.gen_access_token(client_id, client_secret, refresh_token)
    print("Access token: {}".format(access_token))


@chrome.command('upload', short_help="upload a new version of an extension.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('refresh_token', required=True)
@click.argument('app_id', required=True)
@click.argument('filename', required=True)
@click.option('-t', '--filetype', default='crx', type=click.Choice(['crx', 'zip']))
def upload(client_id, client_secret, refresh_token, app_id, filename, filetype):
    logger.debug("upload with parameters:")
    logger.debug("  client_id: {}".format(client_id))
    logger.debug("  client_secret: {}".format(client_secret))
    logger.debug("  refresh_token: {}".format(refresh_token))
    logger.debug("  app_id: {}".format(app_id))
    logger.debug("  filename: {}".format(filename))
    logger.debug("  filetype: {}".format(filetype))

    if filetype == 'crx':
        filename = chrome_store.repack_crx(filename)

    store = chrome_store.ChromeStore(client_id, client_secret, refresh_token, app_id=app_id)
    app_id = store.upload(filename)
    print(app_id)


@chrome.command('create', short_help="upload a brand new extension.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('refresh_token', required=True)
@click.argument('filename', required=True)
@click.option('-t', '--filetype', default='crx', type=click.Choice(['crx', 'zip']))
def create(client_id, client_secret, refresh_token, filename, filetype):
    logger.debug("creating with parameters:")
    logger.debug("  client_id: {}".format(client_id))
    logger.debug("  client_secret: {}".format(client_secret))
    logger.debug("  refresh_token: {}".format(refresh_token))
    logger.debug("  filename: {}".format(filename))
    logger.debug("  filetype: {}".format(filetype))

    if filetype == 'crx':
        filename = chrome_store.repack_crx(filename)

    store = chrome_store.ChromeStore(client_id, client_secret, refresh_token)
    app_id = store.upload(filename, True)
    print(app_id)


@chrome.command('publish', short_help="publish extension to public or trusted audience.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('refresh_token', required=True)
@click.argument('app_id', required=True)
@click.option('--target', type=click.Choice(['public', 'trusted']), required=True)
def publish(client_id, client_secret, refresh_token, app_id, target):
    logger.debug("client_id: {}".format(client_id))
    logger.debug("client_secret: {}".format(client_secret))
    logger.debug("refresh_token: {}".format(refresh_token))
    logger.debug("app_id: {}".format(app_id))
    logger.debug("target: {}".format(target))

    store = chrome_store.ChromeStore(client_id, client_secret, refresh_token, app_id=app_id)
    if target == 'public':
        target = chrome_store.ChromeStore.TARGET_PUBLIC
    elif target == 'trusted':
        target = chrome_store.ChromeStore.TARGET_TRUSTED
    else:
        raise NotImplementedError("Unknown target type: {}".format(target))

    store.publish(target)


@chrome.command('repack', short_help="create a zip from .crx archive")
@click.argument('filename', required=True)
def repack(filename):
    chrome_store.repack_crx(filename, util.work_dir)
