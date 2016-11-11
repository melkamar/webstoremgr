import os
import shutil
import zipfile

import click
import requests
from . import logging_helper

logging_helper.init_logging()
logger = logging_helper.get_logger(__file__)


class Webstore:
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token


class GoogleAuth:
    @staticmethod
    def get_token(client_id, client_secret, code):
        res = requests.post("https://accounts.google.com/o/oauth2/token",
                            data={
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "code": code,
                                "grant_type": "authorization_code",
                                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
                            })
        try:
            res.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            exit(1)

        res_json = res.json()
        return res_json['access_token'], res_json['refresh_token']

    @staticmethod
    def refresh_token():
        # TODO
        pass


def repack_crx(filename):
    """

    Args:
        filename(str): A .crx Chrome Extension file.

    Returns:

    """
    file_dir = os.path.dirname(filename)
    temp_dir = os.path.join(file_dir, "temp_deployer")
    temp_dir = os.path.realpath(temp_dir)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    zip_file = zipfile.ZipFile(filename)
    zip_file.extractall(temp_dir)
    zip_file.close()

    fn_noext = os.path.splitext(filename)
    shutil.make_archive(os.path.join(temp_dir, fn_noext[0]), 'zip', temp_dir)


@click.group()
def main():
    logging_helper.init_logging()


@main.command()
@click.argument('client_id', required=True)
def get_code(client_id):
    print(
        """
    Open this URL in your browser, accept permission request and copy the given code.
    Then run this script again with the <TODO> code.

    https://accounts.google.com/o/oauth2/auth?response_type=code&scope=https://www.googleapis.com/auth/chromewebstore&client_id={}&redirect_uri=urn:ietf:wg:oauth:2.0:oob
    """.format(client_id))


@main.command()
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('code', required=True)
def get_token(client_id, client_secret, code):
    access_token, refresh_token = GoogleAuth.get_token(client_id, client_secret, code)
    print("Received tokens:")
    print("  access_token: {}".format(access_token))
    print("  refresh_token: {}".format(refresh_token))


@main.command()
@click.argument('token', required=True)
@click.argument('app_id', required=True)
@click.argument('filename', required=True)
@click.option('-t', '--filetype', default='crx', type=click.Choice(['crx', 'zip']))
def upload(token, app_id, filename, filetype):
    if filetype == 'crx':
        repack_crx(filename)


if __name__ == '__main__':
    main()
