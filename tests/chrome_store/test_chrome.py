from chrome_store.chrome_store import ChromeStore


def test_redeem_code(betamax_session, auth):
    store = ChromeStore(auth['client_id'], auth['client_secret'], session=betamax_session)
    assert store.refresh_token is None

    store.authenticate(auth['code'])
    print("refresh_token: {}".format(store.refresh_token))
    assert store.refresh_token is not None


def test_gen_access_token(betamax_session, auth):
    store = ChromeStore(auth['client_id'],
                        auth['client_secret'],
                        refresh_token=auth['refresh_token'],
                        session=betamax_session)

    assert store.generate_access_token() is not None
