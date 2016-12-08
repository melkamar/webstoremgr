import click
from webstore_deployer import logging_helper, util, strings
from . import firefox_store

logger = logging_helper.get_logger(__file__)

_download_options = [
    click.option('--interval', default=30,
                 help="Polling interval in seconds to retry downloading given extension from Mozilla store."),
    click.option('--attempts', default=10,
                 help="Number of polling attempts to download given extension from Mozilla store."),
    click.option('--folder', help="Target folder for the download.")
]

_general_options = [
    click.option('--client_id', 'jwt_issuer', required=True,
                 help="JWT issuer field of API credentials in Mozilla developer hub."),
    click.option('--client_secret', 'jwt_secret', required=True,
                 help="JWT secret field of API credentials in Mozilla developer hub."),
    click.option('--addon_id', required=True),
    click.option('--version', required=True)
]


def download_options(func):
    for option in reversed(_download_options):
        func = option(func)
    return func


def general_options(func):
    for option in reversed(_general_options):
        func = option(func)
    return func


@click.group()
def firefox():
    pass


@firefox.command('upload', short_help="Upload a xpi extension on Mozilla store.")
@general_options
@click.option('--filename', required=True, help="File to sign.")
@click.pass_context
def upload(ctx, jwt_issuer, jwt_secret, addon_id, version, filename):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.upload(filename, addon_id, version)


@firefox.command('download', short_help="Download a xpi extension on Mozilla store.")
@general_options
@download_options
@click.pass_context
def download(ctx, jwt_issuer, jwt_secret, addon_id, version, interval, attempts, folder):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.download(addon_id, version, folder, attempts, interval)


@firefox.command('sign', short_help="Sign a xpi extension on Mozilla store and download the signed file.")
@general_options
@click.option('--filename', required=True, help="File to sign.")
@download_options
@click.pass_context
def sign(ctx, jwt_issuer, jwt_secret, addon_id, version, filename, interval, attempts, folder):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.upload(filename, addon_id, version)
    store.download(addon_id, version, folder, attempts, interval)
