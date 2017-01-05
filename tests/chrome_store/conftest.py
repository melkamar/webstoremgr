import betamax
import json
import os
import pytest
import urllib.parse

from betamax.cassette import cassette

placeholder_access_token = '<ACCESS_TOKEN>'
placeholder_refresh_token = '<REFRESH_TOKEN>'

default_client_id = 'fake_client_id'
default_client_secret = 'fake_client_secret'
default_refresh_token = 'fake_refresh_token'
default_code = 'fake_code'
default_app_id = 'fake_app_id'

client_id = os.environ.get('client_id', default_client_id)
client_secret = os.environ.get('client_secret', default_client_secret)
refresh_token = os.environ.get('refresh_token', default_refresh_token)
code = os.environ.get('code', default_code)
app_id = os.environ.get('app_id', default_app_id)


def sanitize_tokens(interaction, current_cassette):
    if interaction.data['response']['status']['code'] != 200:
        return

    try:
        response_body = interaction.data['response']['body']['string']
        json_body = json.loads(response_body)
    except KeyError:
        print("""Response does not contain a string body!
        Interaction:
        {}""".format(interaction.data))
        return

    try:
        access_token = json_body['access_token']
        current_cassette.placeholders.append(
            cassette.Placeholder(placeholder=placeholder_access_token, replace=access_token)
        )
    except KeyError:
        pass

    try:
        refresh_token = json_body['refresh_token']

        current_cassette.placeholders.append(
            cassette.Placeholder(placeholder=placeholder_refresh_token, replace=refresh_token)
        )

    except KeyError:
        pass


@pytest.fixture
def auth():
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'code': code,
        'app_id': app_id,
        'default_client_id': default_client_id,
        'default_client_secret': default_client_secret,
        'default_refresh_token': refresh_token,
        'default_code': default_code,
        'default_app_id': default_app_id,
        'placeholder_access_token': placeholder_access_token,
        'placeholder_refresh_token': placeholder_refresh_token,
    }


@pytest.fixture
def betamax_session(betamax_session):
    betamax_session.headers.update({'Accept-Encoding': 'identity'})
    return betamax_session


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'

    # If all required environment variables are filled, record the cassettes again. Else just use existing ones.
    if client_id != default_client_id \
            and client_secret != default_client_secret \
            and code != default_code \
            and refresh_token != default_refresh_token:
        config.default_cassette_options['record_mode'] = 'all'
    else:
        config.default_cassette_options['record_mode'] = 'none'

    config.define_cassette_placeholder('<CLIENT_ID>', urllib.parse.quote_plus(client_id))
    config.define_cassette_placeholder('<CLIENT_SECRET>', urllib.parse.quote_plus(client_secret))
    config.define_cassette_placeholder('<REFRESH_TOKEN>', urllib.parse.quote_plus(refresh_token))
    config.define_cassette_placeholder('<CODE>', urllib.parse.quote_plus(code))
    config.define_cassette_placeholder('<APP_ID>', urllib.parse.quote_plus(app_id))

    config.before_record(callback=sanitize_tokens)
