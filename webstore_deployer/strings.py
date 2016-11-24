webstore_init_info = """Open this URL in your browser, accept permission request and copy the given code:
    https://accounts.google.com/o/oauth2/auth?response_type=code&scope=https://www.googleapis.com/auth/chromewebstore&client_id={}&redirect_uri=urn:ietf:wg:oauth:2.0:oob

Then run: $ python -m webstore_deployer auth <client_id> <client_secret> <code>."""