import string
import random
import re
import json
import base64
import hashlib
import requests
from bs4 import BeautifulSoup

CONFIG_DESTINATION = 'config.json'
STORAGE_DESTINATION = 'storage.json'

CONFIG = json.loads(open(CONFIG_DESTINATION, 'r').read())

def get_guest_token():
    """Get token to add items to cart etc. No credentials needed."""
    with open(STORAGE_DESTINATION, 'a+') as file:
        try:
            storage = json.load(file)
            token = storage['guest_token']
            if not token:
                token = _fetch_new_guest_token()
                storage['guest_token'] = token
                file.seek(0)
                file.truncate()
                json.dump(storage, file)
        except json.decoder.JSONDecodeError:
            token = _fetch_new_guest_token()
            storage = {
                "guest_token": token,
                "authorized_token": ""
            }
            file.seek(0)
            file.truncate()
            json.dump(storage, file)
    return token

def get_new_guest_token(): # TODO: Real refresh token
    """Technically it just fetches new token and puts it into the storage."""
    token = _fetch_new_guest_token()
    with open(STORAGE_DESTINATION, 'a+') as file:
        try:
            storage = json.load(file)
            storage['guest_token'] = token
            file.seek(0)
            file.truncate()
            json.dump(storage, file)
        except json.decoder.JSONDecodeError:
            storage = {
                "guest_token": token,
                "authorized_token": ""
            }
            file.seek(0)
            file.truncate()
            json.dump(storage, file)
    return token

def _fetch_new_guest_token():
    url = 'https://api.ingka.ikea.com/guest/token'
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Origin': 'https://www.ikea.com',
        'Referer': 'https://www.ikea.com/',
        'Host': 'api.ingka.ikea.com',
        'X-Client-Id': 'e026b58d-dd69-425f-a67f-1e9a5087b87b',
        'X-Client-Secret': 'cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB'
    }
    response = requests.post(url, headers=headers, json={'retailUnit': 'ru'})
    token = response.json()['access_token']
    return token

def create_s256_code_challenge(code_verifier):
    """
    https://github.com/lepture/authlib
    Create S256 code_challenge with the given code_verifier.
    """
    data = hashlib.sha256(bytes(code_verifier.encode('ascii', 'strict'))).digest()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8', 'strict')

def generate_token():
    """https://github.com/lepture/authlib"""
    rand = random.SystemRandom()
    return ''.join(rand.choice(string.ascii_letters + string.digits) for _ in range(48))

def login():
    """
    OAuth2 authorization
    """
    username = CONFIG['username']
    password = CONFIG['password']
    if not username and not password:
        raise Exception('Add username and password in config.json')

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
    }

    # 1. /autorize  Autorize; redirects to /login with useful info
    code_verifier = generate_token()
    code_challenge = create_s256_code_challenge(code_verifier)
    state = generate_token()
    authorize_endpoint = 'https://ru.accounts.ikea.com/authorize?' \
        + 'client_id=72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl' \
        + '&redirect_uri=https%3A%2F%2Fwww.ikea.com%2Fru%2Fru%2Fprofile%2Flogin%2F' \
        + '&response_type=code' \
        + '&ui_locales=ru-RU' \
        + '&code_chalenge=' + code_challenge + '&code_chalenge_method=S256' \
        + '&scope=openid%20profile%20email' \
        + '&audience=https%3A%2F%2Fretail.api.ikea.com&registration=%7B%22bveventid%22%3Anull%7D' \
        + '&consumer=OWF' \
        + '&state=' + state + '&auth0Client=eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0%3D'
    authorize_headers = headers
    authorize_headers['Accept']: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    authorize_response = session.get(authorize_endpoint, headers=authorize_headers)
    encoded_session_config = BeautifulSoup(authorize_response.text, 'html.parser').find('script', id='a0-config').get('data-config')
    session_config = json.loads(base64.b64decode(encoded_session_config))
    # 2. /usernamepassword/login    Log in system
    usrpwd_login_endpoint = 'https://ru.accounts.ikea.com/usernamepassword/login'
    usrpwd_login_payload = {
        'client_id': session_config['clientID'],
        'redirect_uri': session_config['callbackURL'],
        'tenant': session_config['auth0Tenant'],
        'response_type': session_config['extraParams']['response_type'],
        'scope': session_config['extraParams']['scope'],
        'audience': session_config['extraParams']['audience'],
        '_csrf': session_config['extraParams']['_csrf'],
        'state': session_config['extraParams']['state'],
        '_intstate': session_config['extraParams']['_intstate'],
        'username': username,
        'password': password,
        'connection': 'Username-Password-Authentication'
    }
    usrpwd_login_headers = headers
    usrpwd_login_headers |= {
        'Referer': authorize_response.url,
        'Connection': 'keep-alive',
        'Auth0-Client': session_config['extraParams']['auth0Client'],
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-us',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    }
    usrpwd_login_result = session.post(usrpwd_login_endpoint, headers=usrpwd_login_headers, json=usrpwd_login_payload)
    if not usrpwd_login_result.ok:
        raise Exception(usrpwd_login_result.json())

    # 3. /login/callback    Get code parameter from callback
    soup = BeautifulSoup(usrpwd_login_result.text, 'html.parser')
    wctx = soup.find('input', {'name':'wctx'}).get('value')
    wresult = soup.find('input', {'name':'wresult'}).get('value')

    login_callback_endpoint = 'https://ru.accounts.ikea.com/login/callback'
    login_callback_headers = headers
    login_callback_headers |= {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ru.accounts.ikea.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': usrpwd_login_result.url,
        'Accept-Language': 'en-us'
    }
    login_callback_payload = 'wa=wsignin1.0&wresult=%s&wctx=%s' % (wresult, wctx)
    login_callback_response = session.post(login_callback_endpoint, headers=login_callback_headers, data=login_callback_payload)

    # 4. /oauth/token   Get access token
    oauth_token_enpoint = 'https://ru.accounts.ikea.com/oauth/token'
    oauth_token_headers = headers
    oauth_token_headers |= {
        'Content-Type': 'application/json',
        'Origin': 'https://www.ikea.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Referer': login_callback_response.url,
        'Accept-Language': 'en-us'
    }
    oauth_token_payload = {
        'grant_type': 'authorization_code',
        'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
        'code_verifier': code_verifier,
        'code': re.search(r'code=([^"&]+)', login_callback_response.url)[1],
        'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
        'scope': 'openid profile email'
    }
    oauth_token_response = session.post(
        oauth_token_enpoint,
        headers=oauth_token_headers,
        json=oauth_token_payload)
    token = oauth_token_response.json()['access_token']
    return token