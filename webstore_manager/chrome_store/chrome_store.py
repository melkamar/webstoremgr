import os

import requests
from webstore_manager import logging_helper, util
from webstore_manager.constants import ErrorCodes
from webstore_manager.store.store import Store

logger = logging_helper.get_logger(__file__)


class ChromeStore(Store):
    """
    Class representing Chrome Webstore. Holds info about the client, app and its refresh token.
    """

    TARGET_PUBLIC = 0
    TARGET_TRUSTED = 1

    GOOGLE_OAUTH_TOKEN = 'https://www.googleapis.com/oauth2/v4/token'

    def __init__(self, client_id, client_secret, refresh_token=None, app_id="", session=None):
        """
        Args:
            client_id:
            client_secret:
            refresh_token:
            app_id:
            session: If none, a new requests session will be created. Otherwise the supplied one will be used.
        """
        super().__init__(session)
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_id = app_id
        self.refresh_token = refresh_token
        self.update_item_url = "https://www.googleapis.com/upload/chromewebstore/v1.1/items/{}".format(app_id)
        self.new_item_url = "https://www.googleapis.com/upload/chromewebstore/v1.1/items"
        self.publish_item_url = "https://www.googleapis.com/chromewebstore/v1.1/items/{}/publish?publishTarget={{}}".format(
            app_id)
        self.get_status_url = "https://www.googleapis.com/chromewebstore/v1.1/items/{}?projection=draft"

    def publish(self, target):
        """
        Publish an existing extension. It has to be uploaded to the Webstore first, its name is obtained from
        the ChromeStore's app_id field.

        Args:
            target: Target audience to publish to. May be ChromeStore.TARGET_PUBLIC or TARGET_TRUSTED.

        Returns:
            None
        """
        auth_token = self.generate_access_token()

        headers = {"Authorization": "Bearer {}".format(auth_token),
                   "x-goog-api-version": "2",
                   "Content-Length": "0"}

        # Note: webstore API documentation is inconsistent whether it requires publishTarget in headers or in URL
        # so I will use both, to be sure.
        if target == self.TARGET_PUBLIC:
            target = "default"
        elif target == self.TARGET_TRUSTED:
            headers["publishTarget"] = "trustedTesters"
            target = "trustedTesters"
        else:
            logger.error("Unknown publish target: {}".format(target))
            exit(ErrorCodes.chrome_publish_bad_target)

        logger.debug("Making publish query to {}".format(self.publish_item_url.format(target)))
        response = self.session.post(self.publish_item_url.format(target),
                                     headers=headers)

        try:
            res_json = response.json()
            status = res_json['status']

            if len(status) == 0 or (len(status) == 1 and status[0] == 'OK'):
                self.app_id = res_json['item_id']
                logger.info("Publishing completed. Item ID: {}".format(self.app_id))
                return self.app_id
            else:
                logger.error("Status is not empty (something bad happened).")
                logger.error("Response: {}".format(res_json))
                exit(ErrorCodes.chrome_publish_bad_status)

        except KeyError as error:
            logger.error("Key 'status' not found in returned JSON.")
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(ErrorCodes.chrome_upload_key_not_found)
        except ValueError:
            logger.error("Response could not be decoded as JSON.")
            logger.error("Response code: {}".format(response.status_code))
            logger.error("Response: {}".format(response.content))
            exit(ErrorCodes.response_not_json)

    def upload(self, filename, new_item=False):
        """
        Uploads a zip-archived extension to the webstore; either as a completely new extension, or as a
        version update to an existing one.

        Args:
            filename(str): Path to the archive.
            new_item(bool): If true, this is a new extension. If false, this is an update to an existing one.

        Returns:
            str: Item ID of the created or updated extension.
        """
        if new_item:
            logger.info("Uploading a new extension - new file: {}".format(filename))
        else:
            logger.info("Uploading an update - file: {}".format(filename))

        if not new_item and not self.app_id:
            logger.error("To upload a new version of an extension, supply the app_id parameter!")
            exit(ErrorCodes.chrome_upload_no_appid)

        auth_token = self.generate_access_token()

        headers = {"Authorization": "Bearer {}".format(auth_token),
                   "x-goog-api-version": "2"}

        data = open(filename, 'rb')

        if new_item:
            response = self.session.post(self.new_item_url,
                                         headers=headers,
                                         data=data)
        else:
            response = self.session.put(self.update_item_url,
                                        headers=headers,
                                        data=data)

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(ErrorCodes.chrome_upload_generic_error)

        try:
            rjson = response.json()
            state = rjson['uploadState']
            if not state == 'SUCCESS':
                logger.error("Uploading state is not SUCCESS.")
                logger.error("Response: {}".format(rjson))
                exit(ErrorCodes.chrome_upload_app_not_found)
            else:
                self.app_id = rjson['id']
                logger.info("Upload completed. Item ID: {}".format(self.app_id))
                logger.info("Done.")
                return self.app_id

        except KeyError as error:
            logger.error("Key 'uploadState' not found in returned JSON.")
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(ErrorCodes.chrome_upload_key_not_found)

    def get_uploaded_version(self):
        """
        Finds version of an extension that is currently uploaded in the web store.

        Returns:
            str: Version as specified in the original manifest.
        """
        auth_token = self.generate_access_token()

        headers = {"Authorization": "Bearer {}".format(auth_token),
                   "x-goog-api-version": "2",
                   "Content-Length": "0",
                   "Expect": ""}

        final_url = self.get_status_url.format(self.app_id)
        logger.debug("Checking status at {}".format(final_url))
        response = self.session.get(final_url,
                                    headers=headers)

        try:
            res_json = response.json()
            reported_version = res_json['crxVersion']
            reported_state = res_json['uploadState']  # No use right now

            logger.info("Status obtained. Item ID: {}, version: {}, state: {}".format(self.app_id, reported_version,
                                                                                      reported_state))
            return reported_version

        except KeyError as error:
            logger.error("Key 'crxVersion' or 'uploadState' not found in returned JSON.")
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(ErrorCodes.chrome_upload_key_not_found)
        except ValueError:
            logger.error("Response could not be decoded as JSON.")
            logger.error("Response code: {}".format(response.status_code))
            logger.error("Response: {}".format(response.content))
            exit(ErrorCodes.response_not_json)

    def generate_access_token(self):
        """
        Generate a new access token from a saved refresh token.

        Returns:
            Access token.

        """
        auth_token = self.gen_access_token(self.client_id, self.client_secret, self.refresh_token, session=self.session)
        logger.info("Obtained an auth token: {}".format(auth_token))
        return auth_token

    def authenticate(self, code):
        """
        Authenticate by exchanging a given code for a refresh token.

        Save the refresh token as a field of this ChromeStore object.
        Args:
            code: Code obtained from Google.

        Returns:
            None.
        """
        _, self.refresh_token = ChromeStore.redeem_code(self.client_id, self.client_secret, code, self.session)

    @staticmethod
    def redeem_code(client_id, client_secret, code, session=None):
        """
        Obtain access and refresh tokens from Google OAuth from client ID, secret and one-time code.

        Args:
            client_id(str): ID of the client (see developer console - credentials - OAuth 2.0 client IDs).
            client_secret(str): Secret of the client (see developer console - credentials - OAuth 2.0 client IDs).
            code(str): Auth code obtained from confirming access at
                       https://accounts.google.com/o/oauth2/auth?response_type=code&scope=https://www.googleapis.com/auth/chromewebstore&client_id=$CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob.
            session(requests.Session, optional): If set, use this session for HTTP requests.

        Returns:
            str, str: access_token, refresh_token
        """

        logger.debug("Requesting tokens using parameters:")
        logger.debug("    Client ID:     {}".format(client_id))
        logger.debug("    Client secret: {}".format(client_secret))
        logger.debug("    Code:          {}".format(code))

        session = session or requests.Session()
        response = session.post(ChromeStore.GOOGLE_OAUTH_TOKEN,
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
            exit(ErrorCodes.response_error)

        res_json = response.json()
        return res_json['access_token'], res_json['refresh_token']

    @staticmethod
    def gen_access_token(client_id, client_secret, refresh_token, session=None):
        """
        Use refresh token to generate a new client access token.

        Args:
            client_id(str): Client ID field of Developer Console OAuth client credentials.
            client_secret(str): Client secret field of Developer Console OAuth client credentials.
            refresh_token(str): Refresh token obtained when calling get_tokens method.
            session(requests.Session, optional): If set, use this session for HTTP requests.

        Returns:
            str: New user token valid (by default) for 1 hour.
        """
        session = session or requests.Session()
        response = session.post(ChromeStore.GOOGLE_OAUTH_TOKEN,
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
            exit(ErrorCodes.response_error)

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

    util.unzip(filename, temp_dir)

    fn_noext = os.path.basename(os.path.splitext(filename)[0])
    zip_new_name = fn_noext + ".zip"

    if not target_dir:
        full_name = util.make_zip(zip_new_name, temp_dir, util.build_dir)
    else:
        full_name = util.make_zip(zip_new_name, temp_dir, target_dir)
    return full_name
