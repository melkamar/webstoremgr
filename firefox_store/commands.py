import click
from webstore_deployer import logging_helper, util, strings
from webstore_deployer.util import custom_options
from . import firefox_store

logger = logging_helper.get_logger(__file__)

_download_options = [
    click.option('--interval', default=30,
                 help="Polling interval in seconds to retry downloading given extension from Mozilla store."),
    click.option('--attempts', default=10,
                 help="Number of polling attempts to download given extension from Mozilla store."),
    click.option('--folder', help="Target folder for the download.")
]

_jwt_options = [
    click.option('--client_id', 'jwt_issuer', required=True,
                 help="JWT issuer field of API credentials in Mozilla developer hub."),
    click.option('--client_secret', 'jwt_secret', required=True,
                 help="JWT secret field of API credentials in Mozilla developer hub."),
]

_general_options = [
    *_jwt_options,
    click.option('--addon_id', required=True),
    click.option('--version', required=True)
]


@click.group()
def firefox():
    pass


@firefox.command('upload', short_help="Upload a xpi extension on Mozilla store.")
@custom_options(_general_options)
@click.option('--filename', required=True, help="File to sign.")
@click.pass_context
def upload(ctx, jwt_issuer, jwt_secret, addon_id, version, filename):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.upload(filename, addon_id, version)


@firefox.command('download', short_help="Download a xpi extension on Mozilla store.")
@custom_options(_general_options)
@custom_options(_download_options)
@click.pass_context
def download(ctx, jwt_issuer, jwt_secret, addon_id, version, interval, attempts, folder):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.download(addon_id, version, folder, attempts, interval)


@firefox.command('sign', short_help="Sign a xpi extension on Mozilla store and download the signed file.")
@custom_options(_general_options)
@click.option('--filename', required=True, help="File to sign.")
@custom_options(_download_options)
@click.pass_context
def sign(ctx, jwt_issuer, jwt_secret, addon_id, version, filename, interval, attempts, folder):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.upload(filename, addon_id, version)
    store.download(addon_id, version, folder, attempts, interval)


@firefox.command('gen_token', short_help="Generate a JWT token used to authenticate in Mozilla store.")
@custom_options(_jwt_options)
@click.pass_context
def gen_token(ctx, jwt_issuer, jwt_secret):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    token = store.gen_jwt_token()
    print(token)
    logger.info(token)
