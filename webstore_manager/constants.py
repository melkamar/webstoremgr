webstore_init_info = """Open this URL in your browser, accept permission request and copy the given code:
    https://accounts.google.com/o/oauth2/auth?response_type=code&scope=https://www.googleapis.com/auth/chromewebstore&client_id={}&redirect_uri=urn:ietf:wg:oauth:2.0:oob

Then run: $ python -m webstore_manager auth <client_id> <client_secret> <code>."""


class ErrorCodes:
    response_error = 1
    chrome_upload_app_not_found = 2
    chrome_upload_key_not_found = 4
    chrome_upload_generic_error = 3
    chrome_upload_no_appid = 6
    chrome_publish_bad_target = 8
    chrome_publish_bad_status = 9
    response_not_json = 10
