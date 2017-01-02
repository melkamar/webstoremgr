# Original script developed by Filip Masri

import os
import random
import time
import urllib.parse

import jwt
import requests
import re

from webstore_deployer import logging_helper, util
from store.store import Store

logger = logging_helper.get_logger(__file__)


class FFStore(Store):
    """
    Class representing Mozilla Add-on store.

    Provides methods for interacting with it - authenticating and signing extensions.
    """

    def __init__(self, jwt_issuer, jwt_secret, session=None):
        """
        Args:
            jwt_issuer(str): JWT Issuer field obtained in Mozilla's Addon Developer Hub from Manage API keys section.
            jwt_secret(str): JWT Secret field obtained in Mozilla's Addon Developer Hub from Manage API keys section.
        """
        super().__init__(session)
        self.jwt_issuer = jwt_issuer
        self.jwt_secret = jwt_secret

    def _gen_auth_headers(self):
        """
        Generate auth headers to be immediately used by Requests.

        Returns(dict):
            Dictionary of header entries.
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

    @staticmethod
    def parse_manifest(filename):
        """
        Parse Firefox extension id and version from the given xpi file. The attributes are expected to be located in
        `install.rdf` inside <em:id> and <em:version> tags.

        Args:
            filename(str): Name of the xpi file.

        Returns:
            tuple: (id, version)

        Raises:
            KeyError:if ID or Version cannot be parsed from the file.
        """

        temp_dir = os.path.join(util.build_dir, os.path.basename(filename))

        # Extract xpi
        util.unzip(filename, temp_dir)

        # Read install.rdf manifest and parse
        with open(os.path.join(temp_dir, "install.rdf")) as f:
            txt = f.read()
            # ID
            search = re.search(r'<em:id>([^<]*)</em:id>', txt)
            if search:
                ext_id = search.group(1)
            else:
                ext_id = None

            # Version
            search = re.search(r'<em:version>([^<]*)</em:version>', txt)
            if search:
                ext_version = search.group(1)
            else:
                ext_version = None

            if ext_id and ext_version:
                return ext_id, ext_version
            else:
                raise KeyError(
                    "Version or ID could not be parsed. Obtained ID:{}, Version:{}".format(ext_id, ext_version))

    def _get_addon_status(self, addon_id, addon_version):
        """
        Find status of an addon uploaded to the Mozilla store.

        Args:
            addon_id(str): ID of the addon as specified in its install.rdf manifest under <em:id>.
            addon_version(str): Version of the addon as specified in its install.rdf manifest under <em:version>.

        Returns:
            tuple:
               processed(bool):                 True if the extension is signed and ready to be downloaded,
                                                False otherwise.
               urls(:obj:`list` of :obj:`str`): list of URLs from which to download the files associated with the
                                                extension. Will be empty if processed is False.
        """
        url = 'https://addons.mozilla.org/api/v3/addons/{}/versions/{}/'.format(addon_id, addon_version)

        headers = self._gen_auth_headers()
        response = requests.get(url,
                                headers=headers)

        try:
            util.handle_requests_response_status(response)
        except requests.HTTPError:
            exit(3)

        processed = util.read_json_key(response.json(), 'processed')

        urls = []
        if processed:
            files = util.read_json_key(response.json(), 'files')
            urls = [util.read_json_key(file, 'download_url') for file in files]

        return processed, urls

    def download(self, addon_id, addon_version, folder="", attempts=1, interval=10, target_name=""):
        """
        Downloads an extension from the store. In case the extension is not processed (signed etc.) yet,
        the store will be polled several times to try and download it.

        Args:
            addon_id(str): ID of the addon as specified in its install.rdf manifest under <em:id>.
            addon_version(str): Version of the addon as specified in its install.rdf manifest under <em:version>.
            folder(str, optional): Destination folder where to place the downloaded file(s).
            attempts(int, optional): Number of polling attempts to do.
            interval(int, optional): Interval in seconds between polling attempts.

        Returns:
            bool: True if extension was downloaded correctly, False otherwise.
        """
        logger.info(
            "Downloading extension. ID: {}, version: {}. Polling every {} seconds up to {} times.".format(addon_id,
                                                                                                          addon_version,
                                                                                                          interval,
                                                                                                          attempts))

        processed = False
        urls = []
        for attempt_nr in range(0, attempts):
            processed, urls = self._get_addon_status(addon_id, addon_version)

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

            if len(urls) == 1 and target_name:
                logger.warn("Target name provided and a single file is being downloaded. Ignoring URL name and saving "
                            "as: {}.".format(target_name))
                filename = target_name
            else:
                filename = os.path.basename(urllib.parse.urlparse(url).path)

            full_path = os.path.join(folder, filename)
            logger.info("Writing into file {}".format(full_path))
            with open(full_path, 'wb') as f:
                f.write(response.content)

        return True

    def upload(self, filename, addon_id, addon_version):
        """
        Upload a xpi extension to the store and automatically sign it.

        Note that the extension will not be signed instantaneously. Some automatic checks are performed and it takes
        a while.

        Args:
            filename(str): Filename of the extension on the disk.
            addon_id(str): ID of the addon as specified in its install.rdf manifest under <em:id>.
            addon_version(str): Version of the addon as specified in its install.rdf manifest under <em:version>.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        # If no version was specified, try parsing it from the file.
        if not addon_version:
            parsed_version = self.parse_manifest(filename)
            if not parsed_version:
                logger.error("Version could not be parsed from file {}. Check the install.rdf file or specify the "
                             "version yourself.".format(filename))
                return False
            addon_version = parsed_version

        logger.info("Uploading file {}. ID: {}, version: {}.".format(filename, addon_id, addon_version))

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

        return True
