import os
import shutil
import zipfile

import click
import requests
from . import logging_helper
from . import strings
from . import util

logging_helper.init_logging()
logger = logging_helper.get_logger(__file__)


class Webstore:
    """
    Class representing Chrome Webstore. Holds info about the client, app and its refresh token.
    """

    def __init__(self, client_id, client_secret, refresh_token, app_id=""):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_id = app_id
        self.refresh_token = refresh_token
        self.update_item_url = "https://www.googleapis.com/upload/chromewebstore/v1.1/items/{}".format(app_id)
        self.new_item_url = "https://www.googleapis.com/upload/chromewebstore/v1.1/items"

    def upload(self, filename, new_item=False):
        """
        Uploads a zip-archived extension to the webstore.

        Args:
            filename(str): Path to the archive.
            new_item(bool): If true, this is a new extension. If false, this is an update to an existing one.

        Returns:
            Null
        """
        if not new_item and not self.app_id:
            logger.error("To upload a new version of an extension, supply the app_id parameter!")
            exit(6)

        auth_token = self.generate_access_token()

        headers = {"Authorization": "Bearer {}".format(auth_token),
                   "x-goog-api-version": "2"}

        data = open(filename, 'rb')

        if new_item:
            response = requests.post(self.new_item_url,
                                     headers=headers,
                                     data=data)
        else:
            response = requests.put(self.update_item_url,
                                    headers=headers,
                                    data=data)

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(3)

        try:
            rjson = response.json()
            state = rjson['uploadState']
            if not state == 'SUCCESS':
                logger.error("Uploading state is not SUCCESS.")
                logger.error("Response: {}".format(rjson))
                exit(2)
            else:
                logger.info("Upload completed. Item ID: {}".format(rjson['id']))
        except KeyError as error:
            logger.error("Key 'uploadState' not found in returned JSON.")
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(4)

    def generate_access_token(self):
        auth_token = GoogleAuth.gen_access_token(self.client_id, self.client_secret, self.refresh_token)
        logger.info("Obtained an auth token: {}".format(auth_token))
        return auth_token


class GoogleAuth:
    @staticmethod
    def get_tokens(client_id, client_secret, code):
        """
        Obtain access and refresh tokens from Google OAuth from client ID, secret and one-time code.

        Args:
            client_id(str): ID of the client (see developer console - credentials - OAuth 2.0 client IDs).
            client_secret(str): Secret of the client (see developer console - credentials - OAuth 2.0 client IDs).
            code(str): Auth code obtained from confirming access at https://accounts.google.com/o/oauth2/auth?response_type=code&scope=https://www.googleapis.com/auth/chromewebstore&client_id=$CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob.

        Returns:
            str, str: access_token, refresh_token
        """

        logger.debug("Requesting tokens using parameters:")
        logger.debug("    Client ID:     {}".format(client_id))
        logger.debug("    Client secret: {}".format(client_secret))
        logger.debug("    Code:          {}".format(code))

        response = requests.post("https://accounts.google.com/o/oauth2/token",
                                 data={
                                     "client_id": client_id,
                                     "client_secret": client_secret,
                                     "code": code,
                                     "grant_type": "authorization_code",
                                     "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
                                 })
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(1)

        res_json = response.json()
        return res_json['access_token'], res_json['refresh_token']

    @staticmethod
    def gen_access_token(client_id, client_secret, refresh_token):
        """
        Use refresh token to generate a new client access token.

        Args:
            client_id(str): Client ID field of Developer Console OAuth client credentials.
            client_secret(str): Client secret field of Developer Console OAuth client credentials.
            refresh_token(str): Refresh token obtained when calling get_tokens method.

        Returns:
            str: New user token valid (by default) for 1 hour.
        """
        response = requests.post("https://accounts.google.com/o/oauth2/token",
                                 data={"client_id": client_id,
                                       "client_secret": client_secret,
                                       "refresh_token": refresh_token,
                                       "grant_type": "refresh_token",
                                       "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
                                       }
                                 )

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(1)

        res_json = response.json()
        return res_json['access_token']


def repack_crx(filename):
    """
    Repacks the given .crx file into a .zip file. Will physically create the file on disk.

    Args:
        filename(str): A .crx Chrome Extension file.

    Returns:
        str: Filename of the newly created zip file.
    """
    file_dir = os.path.dirname(filename)
    temp_dir = os.path.join(file_dir, "temp_deployer")
    temp_dir = os.path.realpath(temp_dir)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    zip_file = zipfile.ZipFile(filename)
    logger.debug("Extracting {} to path {}".format(filename, temp_dir))
    zip_file.extractall(temp_dir)
    zip_file.close()

    fn_noext = os.path.splitext(filename)
    zip_new_name = os.path.join(temp_dir, fn_noext[0]) + ".zip"
    logger.info("Creating zipfile {}".format(zip_new_name))

    util.make_zip(zip_new_name, temp_dir)
    # Todo clean up after the script ends
    return "{}".format(zip_new_name)


@click.group()
def main():
    pass


@main.command()
@click.argument('client_id', required=True)
def init(client_id):
    print(strings.webstore_init_info.format(client_id))


@main.command()
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('code', required=True)
def auth(client_id, client_secret, code):
    access_token, refresh_token = GoogleAuth.get_tokens(client_id, client_secret, code)
    print("Received tokens:")
    print("  access_token: {}".format(access_token))
    print("  refresh_token: {}".format(refresh_token))


@main.command()
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
        filename = repack_crx(filename)

    logger.info("Uploading file {}".format(filename))
    store = Webstore(client_id, client_secret, refresh_token, app_id=app_id)
    store.upload(filename)
    logger.info("Done.")


@main.command()
@click.argument('filename', required=True)
def repack(filename):
    repack_crx(filename)


@main.command()
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
        filename = repack_crx(filename)

    logger.info("Uploading file {}".format(filename))
    store = Webstore(client_id, client_secret, refresh_token)
    store.upload(filename, True)
    logger.info("Done.")


if __name__ == '__main__':
    main()
