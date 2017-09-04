import click
from . import firefox_store
from webstore_manager import logging_helper
from webstore_manager.util import custom_options

logger = logging_helper.get_logger(__file__)

_upload_options = [
    click.option('--filename', required=True, help="File to sign."),
    click.option('--addon-id', 'addon_id', required=False,
                 help="ID of the extension. If not provided, it will be parsed from the file."),
    click.option('--version', required=False,
                 help="Version of the extension. If not provided, it will be parsed from the file.")
]

_download_options = [
    click.option('--interval', default=30,
                 help="Polling interval in seconds to retry downloading given extension from Mozilla store."),
    click.option('--attempts', default=10,
                 help="Number of polling attempts to download given extension from Mozilla store."),
    click.option('--folder', help="Target folder for the download."),
    click.option('--target-name', 'target_name',
                 help="Target filename to save the extension as. Only applicable if the downloads "
                      "contains a single file. It is ignored otherwise."),
]

_jwt_options = [
    click.option('--id', 'jwt_issuer', required=True,
                 help="JWT issuer field of API credentials in Mozilla developer hub."),
    click.option('--secret', 'jwt_secret', required=True,
                 help="JWT secret field of API credentials in Mozilla developer hub."),
]

_general_options = [
    *_jwt_options,
]


@click.group()
def firefox():
    pass


@firefox.command('upload', short_help="Upload a xpi extension on Mozilla store.")
@custom_options(_jwt_options)
@custom_options(_upload_options)
@click.pass_context
def upload(ctx, jwt_issuer, jwt_secret, filename, addon_id, version):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)

    store.upload(filename, addon_id, version)


@firefox.command('download', short_help="Download a xpi extension on Mozilla store.")
@custom_options(_jwt_options)
@click.option('--addon_id', required=True, help="ID of the extension.")
@click.option('--version', required=True, help="Version of the extension.")
@custom_options(_download_options)
@click.pass_context
def download(ctx, jwt_issuer, jwt_secret, addon_id, version, interval, attempts, folder, target_name):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    store.download(addon_id, version, folder, attempts, interval, target_name=target_name)


@firefox.command('sign', short_help="Sign a xpi extension on Mozilla store and download the signed file.")
@custom_options(_general_options)
@custom_options(_upload_options)
@custom_options(_download_options)
@click.pass_context
def sign(ctx, jwt_issuer, jwt_secret, addon_id, version, filename, interval, attempts, folder, target_name):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)

    if not addon_id or not version:
        parsed_id, parsed_version = store.parse_manifest(filename)
        if not addon_id:
            addon_id = parsed_id
        if not version:
            version = parsed_version

    store.upload(filename, addon_id, version)
    store.download(addon_id, version, folder, attempts, interval, target_name=target_name)


@firefox.command('gen-token', short_help="Generate a JWT token used to authenticate in Mozilla store.")
@custom_options(_jwt_options)
@click.pass_context
def gen_token(ctx, jwt_issuer, jwt_secret):
    store = firefox_store.FFStore(jwt_issuer, jwt_secret)
    token = store.gen_jwt_token()
    print(token)
    logger.info(token)
