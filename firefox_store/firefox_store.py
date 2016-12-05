# Original development by Filip Masri

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

    def upload(self, filename, addon_id, version):
        url = 'https://addons.mozilla.org/api/v3/addons/{}/versions/{}/'.format(addon_id, version)

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

    def _get_addon_status(self, addon_id, version):
        url = 'https://addons.mozilla.org/api/v3/addons/{}/versions/{}/'.format(addon_id, version)

        headers = self._gen_auth_headers()
        response = requests.get(url,
                                headers=headers)

        util.check_requests_response_status(response)

        processed = util.read_json_key(response.json(), 'processed')
        files = util.read_json_key(response.json(), 'files')

        # logger.debug(json.dumps(response.json()))
        return processed, files

    def check_status(self, addon_id, version):
        """
        Check signing status of an uploaded addon.

        Args:
            addon_id(str): ID of the addon to check.
            version(str): Version of the addon to check.

        Returns:
            bool: True if addon is processed, signed and ready to download. False otherwise (in which case wait before
            retrying).
        """

        processed, _ = self._get_addon_status(addon_id, version)
        return processed

    def get_download_urls(self, addon_id, version):
        """
        Get URLs for downloading addon files. If files are not finished processing yet, nothing is returned.

        Args:
            addon_id(str): ID of the addon to download.
            version(str): Version of the addon to download.

        Returns:
            (list): List of URLs to download if processed. Empty if no files to download or is not finished
            processing yet.
        """
        processed, files = self._get_addon_status(addon_id, version)

        if not processed:
            logger.info("Addon is not processed yet. Wait for a bit and try again.")
            return False

        urls = [util.read_json_key(file, 'download_url') for file in files]
        return urls

    def download(self, addon_id, version, folder=""):
        urls = self.get_download_urls(addon_id, version)
        if not urls:
            logger.warn("Addon is not processed yet. Wait for a bit and try again.")
            return False

        if not folder:
            folder = util.build_dir

        headers = self._gen_auth_headers()
        for url in urls:
            response = requests.get(url,
                                    headers=headers)

            filename = os.path.basename(urllib.parse.urlparse(url).path)
            full_path = os.path.join(folder, filename)
            logger.info("Writing into file {}".format(full_path))
            with open(full_path, 'wb') as f:
                f.write(response.content)


addonid = 'testtest@melka'
version = '1.1.6'

jwt_issuer = 'user:12694088:77'
jwt_secret = 'b7907f0b9609eb2e5036e4785b13f6fde20f3a63c1bb78c73e5fe3e8ce5d6350'

# FFStore().upload('c:\\Users\\melka\\Downloads\\xpi\\testext.xpi')
ff_store = FFStore(jwt_issuer, jwt_secret)
# ff_store.upload('c:\\Users\\melka\\Downloads\\xpi\\testext.xpi', addonid, version)
# addon_processed = ff_store.check_status(addonid, version)
# logger.warn("Addon processed: {}".format(addon_processed))

# logger.info(ff_store.get_download_urls(addonid, version))
# FFStore().download("https://addons.mozilla.org/api/v3/file/549075/melka_test-1.1.4-fx.xpi?src=api")
ff_store.download(addonid, version)


"""
'iss': 'user:12694088:77',
secret = 'b7907f0b9609eb2e5036e4785b13f6fde20f3a63c1bb78c73e5fe3e8ce5d6350'
"""

# Uploaded file

# files = {'upload': (xpi, open(xpi, 'rb'))}
#
#         headers = {"Authorization" : "JWT {0}".format(getToken())}
#         req = requests.Request('PUT', url, headers=headers, files=files)
#
#         #Prepared request
#         prepared = req.prepare()
#
#         s = requests.Session()
#         res = s.send(prepared)
#
#         res = res.json()
#
#         print "Response from server: {0}".format(res)
#
#         if ("errors" in res) or ("error" in res):
#                 print "Failed to upload adddon"
#                 sys.exit(1)
#
#         else:
#                 print "\nUpload should have been successfull."
#         #res = requests.put(url, files=files, data=data, headers=headers)
#
#         #print data
#         #return res.json()











# import urllib2
# import urllib
# import optparse
# import sys
#
#
# def getToken():
#         """
#         Generate access token in order to sends requests to Mozilla REST API
#         """
#
#         #Time since 1970
#         issuedAt = int(time.time())
#
#         payload = {
#         'iss' : 'user:11952200:801',
# #       'iss' : 'user:12052853:172',
#         'jti' : random.random(),
#         'iat' : issuedAt,
#         'exp' : issuedAt + 60,
#         }
#
# #       secret = '8e6a564adb4ceda0eb3c18992e47c7a5bdad19305c0163e931faa67b131006e5'
#         secret = '6229eee65c4140528b8583e82a48e515e91e5dff628b27c6cde64979861518e1'
#         return jwt.encode(payload, secret, algorithm='HS256')
#
#
#
#
# def downloadAddon(addonid, version, output):
#         """
#         python2.7 extensionManager.py --action=download --addonid=wrc@avast.com --version=10.3.3.43 --output=my.xpi
#         """
#         counter = 0
#
#         while counter != 10:
#
#                 request = urllib2.Request("https://addons.mozilla.org/api/v3/addons/{0}/versions/{1}/".format(addonid, version))
#                 request.add_header("Authorization", "JWT {0}".format(getToken()))
#
#                 response = urllib2.urlopen(request)
#                 response = json.loads(response.read())
#                 print "Response from server: {0}".format(response)
#
#                 try:
#                         durl = response["files"][0]["download_url"]
#                         downloadMovedLink(durl, output)
#                         return
#                 except:
#                         counter += 1
#                         time.sleep(30)
#
#         print "\nCould not download addon!!"
#         sys.exit(1)
#
# def downloadMovedLink(durl, output):
#         """
#         Download xpi from redirected site
#         """
#         request = urllib2.Request(durl)
#         request.add_header("Authorization", "JWT {0}".format(getToken()))
# # It seems link is not redirected anymore
# #        response = urllib2.urlopen(urllib2.urlopen(request).geturl())
#         response = urllib2.urlopen(request)
#
#         f = open(output, "w")
#         xpi = response.read()
#         f.write(xpi)
#         f.close()
#         print "\n.xpi was successfully downloaded."
#
#
# def uploadAddon(addonid, version, xpi):
#         """
#         python2.7 extensionManager.py --action=upload --addonid=wrc@avast.com --version=10.3.3.43 --xpi=source.xpi
#
#         """
#
#         #using rather requests module to issue PUT method
#         import requests
#
#         url = "https://addons.mozilla.org/api/v3/addons/{0}/versions/{1}/".format(addonid, version)
#
#         #Uploaded file
#         files = {'upload': (xpi, open(xpi, 'rb'))}
#
#         headers = {"Authorization" : "JWT {0}".format(getToken())}
#         req = requests.Request('PUT', url, headers=headers, files=files)
#
#         #Prepared request
#         prepared = req.prepare()
#
#         s = requests.Session()
#         res = s.send(prepared)
#
#         res = res.json()
#
#         print "Response from server: {0}".format(res)
#
#         if ("errors" in res) or ("error" in res):
#                 print "Failed to upload adddon"
#                 sys.exit(1)
#
#         else:
#                 print "\nUpload should have been successfull."
#         #res = requests.put(url, files=files, data=data, headers=headers)
#
#         #print data
#         #return res.json()
#
#
# def init_parser():
#     """
#     :return: OptionParser
#     """
#
#     _parser = optparse.OptionParser()
#     _parser.add_option('--action', dest="action", type="str", help='Action to perform [download/upload]')
#     _parser.add_option('--addonid', dest="addonid", type="str", help='Id of adddon to be updated')
#     _parser.add_option('--version', dest='version', type="str", help='Version of the addon to be updated')
#     _parser.add_option('--output', dest='output', type="str", help='Specifies where to save downloaded xpi')
#     _parser.add_option('--xpi', dest='xpi', type="str", help='Path to xpi which is being uploaded')
#
#     return _parser
#
#
# if __name__=="__main__":
#
#         parser = init_parser()
#
#         # Retreive instance variables from parser
#         options, args = parser.parse_args()
#
#         # Transform instance variables to a dictionary
#         vars_dict = dict(vars(options))
#
#         if vars_dict['action'] == "download":
#                 if (vars_dict["addonid"] is None) or (vars_dict["version"] is None) or (vars_dict["output"] is None):
#                         print "addonid, version and output paramaters must be specified when downloading.\nfor help try --help"
#                         sys.exit(1)
#                 downloadAddon(vars_dict["addonid"], vars_dict["version"], vars_dict["output"])
#
#         if vars_dict['action'] == "upload":
#                 if (vars_dict["addonid"] is None) or (vars_dict["version"] is None) or (vars_dict["xpi"] is None):
#                         print "addonid, version and xpi parameters must be specified when uploading.\nfor help try --help"
#                         sys.exit(1)
#
#                 uploadAddon(vars_dict["addonid"], vars_dict["version"], vars_dict["xpi"])
#
#
