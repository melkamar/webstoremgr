# Original script developed by Filip Masri

import os
import random
import time
import urllib.parse

import jwt
import requests
from webstore_deployer import logging_helper, util

logger = logging_helper.get_logger(__file__)


class FFStore:
    def __init__(self, jwt_issuer, jwt_secret):
        super().__init__()
        self.jwt_issuer = jwt_issuer
        self.jwt_secret = jwt_secret

    def upload(self, filename, addon_id, addon_version):
        url = 'https://addons.mozilla.org/api/v3/addons/{}/versions/{}/'.format(addon_id, addon_version)

        headers = self._gen_auth_headers()
        files = {'upload': open(filename, 'rb')}

        logger.debug("""
        URL: {}
        Headers: {}
        Files: {}
        """.format(url, headers, files))

        response = requests.put(url,
                                headers=headers,
                                files=files)

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error(error)
            logger.error("Response: {}".format(response.json()))
            exit(3)

        try:
            # Check if returned info is what we expect (guid should match the addon ID)
            res_json = response.json()
            guid = res_json['guid']
            if guid != addon_id:
                logger.error("Returned guid is not equal to addon ID.")
                logger.error(response.json())
                exit(5)
        except KeyError as error:
            logger.error("Key 'guid' not found in returned JSON.")
            logger.error(error)
            exit(4)

        logger.debug("Response json: {}".format(response.json()))
        logger.info("File {} uploaded for signing.".format(filename))

    def _gen_auth_headers(self):
        """
        Generate auth headers to be immediately used by Requests.

        Returns(dict): Dictionary of header entries.

        """
        return {"Authorization": "JWT {0}".format(self.gen_jwt_token())}

    def gen_jwt_token(self):
        """
        Generate JWT token to be used for authenticated requests to Mozilla.

        Returns:
            str: Encoded JWT token as a text (not bytes).
        """

        # Time since 1970
        issued_at = int(time.time())

        payload = {
            'iss': '{}'.format(self.jwt_issuer),
            'jti': random.random(),
            'iat': issued_at,
            'exp': issued_at + 60,
        }

        secret = self.jwt_secret
        encoded_jwt = jwt.encode(payload, secret, algorithm='HS256')
        return encoded_jwt.decode()  # Convert byte-array to string

    def get_addon_status(self, addon_id, addon_version):
        url = 'https://addons.mozilla.org/api/v3/addons/{}/versions/{}/'.format(addon_id, addon_version)

        headers = self._gen_auth_headers()
        response = requests.get(url,
                                headers=headers)

        util.check_requests_response_status(response)

        processed = util.read_json_key(response.json(), 'processed')

        urls = []
        if processed:
            files = util.read_json_key(response.json(), 'files')
            urls = [util.read_json_key(file, 'download_url') for file in files]

        return processed, urls

    def download(self, addon_id, addon_version, folder="", attempts=1, interval=10):
        processed = False
        urls = []
        for attempt_nr in range(0, attempts):
            processed, urls = self.get_addon_status(addon_id, addon_version)

            # Check both processed flag and if urls is not empty.
            # FF store may sometimes return processed=True but empty URL list, which is only filled up at the next call.
            if processed and urls:
                break
            else:
                logger.warn(
                    "Attempt {}/{}: addon is not processed or no URLs obtained. Will retry in {} seconds.".format(
                        attempt_nr + 1,
                        attempts,
                        interval))
                time.sleep(interval)

        if not processed:
            logger.error("Addon was not processed in time. Consider increasing number of attempts or interval.")
            return False
        else:
            logger.debug("Addon processed, proceed with download. Obtained URLs: {}".format(urls))

        if not folder:
            folder = util.build_dir

        # if folder does not exist, create it
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        headers = self._gen_auth_headers()
        for url in urls:
            logger.debug("Downloading file from url: {}".format(url))
            response = requests.get(url,
                                    headers=headers)

            filename = os.path.basename(urllib.parse.urlparse(url).path)
            full_path = os.path.join(folder, filename)
            logger.info("Writing into file {}".format(full_path))
            with open(full_path, 'wb') as f:
                f.write(response.content)

        return True