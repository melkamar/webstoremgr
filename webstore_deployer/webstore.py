import os
import shutil
import zipfile

import click
import requests
from . import logging_helper
from . import strings
from . import util

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
        self.publish_item_url = "https://www.googleapis.com/chromewebstore/v1.1/items/{}/publish?publishTarget={{}}".format(
            app_id)

    def publish(self, target):
        auth_token = self.generate_access_token()

        headers = {"Authorization": "Bearer {}".format(auth_token),
                   "x-goog-api-version": "2",
                   "Content-Length": "0"}

        # Note: webstore API documentation is inconsistent whether it requires publishTarget in headers or in URL
        # so I will use both, to be sure.
        if target == "public":
            target = "default"
        elif target == "trusted":
            headers["publishTarget"] = "trustedTesters"
            target = "trustedTesters"
        else:
            logger.error("Unknown publish target: {}".format(target))
            exit(8)

        logger.debug("Making publish query to {}".format(self.publish_item_url.format(target)))
        response = requests.post(self.publish_item_url.format(target),
                                 headers=headers)

        try:
            res_json = response.json()
            status = res_json['status']
            if status:
                logger.error("Status is not empty (something happened:)")
                logger.error("Response: {}".format(res_json))
                exit(9)
            else:
                logger.info("Publishing completed. Item ID: {}".format(res_json['id']))
        except KeyError as error:
            logger.error("Key 'status' not found in returned JSON.")
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(4)
        except ValueError:
            logger.error("Response could not be decoded as JSON.")
            logger.error("Response code: {}".format(response.status_code))
            logger.error("Response: {}".format(response.content))
            exit(10)

    def upload(self, filename, new_item=False):
        """
        Uploads a zip-archived extension to the webstore.

        Args:
            filename(str): Path to the archive.
            new_item(bool): If true, this is a new extension. If false, this is an update to an existing one.

        Returns:
            Null
        """
        if new_item:
            logger.info("Uploading a new extension - new file: {}".format(filename))
        else:
            logger.info("Uploading an update - file: {}".format(filename))

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

        logger.info("Done.")

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


def repack_crx(filename, target_dir=""):
    """
    Repacks the given .crx file into a .zip file. Will physically create the file on disk.

    Args:
        filename(str): A .crx Chrome Extension file.
        target_dir(str, optional): If set, zip file will be created in the given directory (instead of temporary dir).

    Returns:
        str: Filename of the newly created zip file. (full path)
    """
    temp_dir = util.build_dir

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    zip_file = zipfile.ZipFile(filename)
    logger.debug("Extracting {} to path {}".format(filename, temp_dir))
    zip_file.extractall(temp_dir)
    zip_file.close()

    fn_noext = os.path.basename(os.path.splitext(filename)[0])
    zip_new_name = fn_noext + ".zip"

    if not target_dir:
        full_name = util.make_zip(zip_new_name, temp_dir, util.build_dir)
    else:
        full_name = util.make_zip(zip_new_name, temp_dir, target_dir)
    return full_name


@click.group()
@click.option('-v', '--verbose', count=True,
              help="Much verbosity. May be repeated multiple times. More v's, more info!")
def main(verbose):
    # TODO remove this, let user decide the verbosity level.
    verbose = 2

    logger.info("Setting level -> {}".format(30 - verbose * 10))
    logging_helper.set_level(30 - verbose * 10)


@main.command('init', short_help="initialize API key. Run this first.")
@click.argument('client_id', required=True)
def init(client_id):
    print(strings.webstore_init_info.format(client_id))


@main.command('auth', short_help="exchange code for auth token. Run this after init.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('code', required=True)
def auth(client_id, client_secret, code):
    access_token, refresh_token = GoogleAuth.get_tokens(client_id, client_secret, code)
    print("Received tokens:")
    print("  access_token: {}".format(access_token))
    print("  refresh_token: {}".format(refresh_token))


@main.command('gen-token', short_help="generate new access token from refresh token.")
@click.argument('client_id', required=True)
@click.argument('client_secret', required=True)
@click.argument('refresh_token', required=True)
def gen_token(client_id, client_secret, refresh_token):
    access_token = GoogleAuth.gen_access_token(client_id, client_secret, refresh_token)
    print("Access token: {}".format(access_token))


@main.command('upload', short_help="upload a new version of an extension.")
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

    store = Webstore(client_id, client_secret, refresh_token, app_id=app_id)
    store.upload(filename)


@main.command('create', short_help="upload a brand new extension.")
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

    store = Webstore(client_id, client_secret, refresh_token)
    store.upload(filename, True)


@main.command('publish', short_help="publish extension to public or trusted audience.")
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

    store = Webstore(client_id, client_secret, refresh_token, app_id=app_id)
    store.publish(target)


@main.command('repack', short_help="create a zip from .crx archive")
@click.argument('filename', required=True)
def repack(filename):
    repack_crx(filename, util.work_dir)


if __name__ == '__main__':
    main()
