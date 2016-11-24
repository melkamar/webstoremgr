import asyncio
import json
import os
import shutil
import zipfile

import aiohttp
import click
from . import logging_helper

logging_helper.init_logging()
logger = logging_helper.get_logger(__file__)


class Webstore:
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token


class GoogleAuth:
    @staticmethod
    def get_tokens(client_id, client_secret, code):
        async def do_post():
            async with aiohttp.ClientSession() as session:
                # async with session.post("https://accounts.google.com/o/oauth2/token",
                #                         data={
                #                             "client_id": client_id,
                #                             "client_secret": client_secret,
                #                             "code": code,
                #                             "grant_type": "authorization_code",
                #                             "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
                #                         }) as response:
                #     logger.warn("Response status code: {}".format(response.status))
                #     return await response.text()

                for i in range(0, 10):
                    async with session.get("http://ccm.net/faq/7859-google-chrome-takes-too-long-to-load-a-page") as response:
                        logger.warn(await response.read())
                return "done."

        loop = asyncio.get_event_loop()

        import time
        start = time.time()
        result = loop.run_until_complete(do_post())
        stop = time.time()
        print(stop-start)

        logger.warn("Async returned: {}".format(result))
        exit(0)
        # res = requests.post("https://accounts.google.com/o/oauth2/token",
        #                     data={
        #                         "client_id": client_id,
        #                         "client_secret": client_secret,
        #                         "code": code,
        #                         "grant_type": "authorization_code",
        #                         "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
        #                     })
        # try:
        #     res.raise_for_status()
        # except requests.HTTPError as error:
        #     logger.error(error)
        #     exit(1)
        #
        # res_json = res.json()
        res_json = json.loads(result)
        return res_json['access_token'], res_json['refresh_token']

    @staticmethod
    def use_refresh_token(client_id, client_secret, refresh_token):
        """
        Use refresh token to generate a new client access token.
        Args:
            client_id(str): Client ID field of Developer Console OAuth client credentials.
            client_secret(str): Client secret field of Developer Console OAuth client credentials.
            refresh_token(str): Refresh token obtained when calling get_tokens method.

        Returns:
            str: New user token valid (by default) for 1 hour.
        """
        res = requests.post("https://accounts.google.com/o/oauth2/token",
                            data={"client_id": client_id,
                                  "client_secret": client_secret,
                                  "refresh_token": refresh_token,
                                  "grant_type": "refresh_token",
                                  "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
                                  }
                            )

        try:
            res.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            exit(1)

        res_json = res.json()
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
    zip_file.extractall(temp_dir)
    zip_file.close()

    fn_noext = os.path.splitext(filename)
    zip_new_name = os.path.join(temp_dir, fn_noext[0])
    logger.info("Creating zipfile {}.zip".format(zip_new_name))
    shutil.make_archive(zip_new_name, 'zip', temp_dir)

    return "{}.zip".format(zip_new_name)


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
    if filetype == 'crx':
        filename = repack_crx(filename)

    logger.info("Uploading file {}".format(filename))

    auth_token = GoogleAuth.use_refresh_token(client_id, client_secret, refresh_token)
    logger.info("Obtained auth token: {}".format(auth_token))


if __name__ == '__main__':
    main()
