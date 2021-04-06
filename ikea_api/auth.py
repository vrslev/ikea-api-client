import string
import json
from random import SystemRandom
from base64 import urlsafe_b64encode, b64decode
from hashlib import sha256
from urllib.parse import urlparse, parse_qs

from requests import Session, post
from bs4 import BeautifulSoup

from .constants import Constants
from .utils import check_response


def get_guest_token():
    """Token expires in 30 days"""
    url = 'https://api.ingka.ikea.com/guest/token'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-us',
        'Origin': 'https://www.ikea.com',
        'Referer': 'https://www.ikea.com/',
        'Connection': 'keep-alive',
        'User-Agent': Constants.USER_AGENT,
        'X-Client-Id': 'e026b58d-dd69-425f-a67f-1e9a5087b87b',
        'X-Client-Secret': 'cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB'
    }
    payload = {'retailUnit': 'ru'}
    response = post(url, headers=headers, json=payload)
    check_response(response)
    token = response.json()['access_token']
    return token


class Auth:
    """
    OAuth2 authorization
    Token expires in 24 hours
    """

    def __init__(self, username, password):
        self.session = Session()
        self.session.headers.update({
            'Accept-Language': 'en-us',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': Constants.USER_AGENT
        })
        auth0_authorize = self._auth0_authorize()
        usernamepassword_login = self._usernamepassword_login(
            username, password, auth0_authorize['session_config'], auth0_authorize['url'])
        login_callback = self._login_callback(
            usernamepassword_login['wctx'], usernamepassword_login['wresult'], usernamepassword_login['url'])
        oauth_token = self._oauth_token(
            login_callback['code'], login_callback['url'])
        self.token = oauth_token

    def _create_s256_code_challenge(self, code_verifier):
        """
        https://github.com/lepture/authlib
        Create S256 code_challenge with the given code_verifier.
        """
        data = sha256(
            bytes(code_verifier.encode('ascii', 'strict'))).digest()
        return urlsafe_b64encode(data).rstrip(b'=').decode('utf-8', 'strict')

    def _generate_token(self):
        """https://github.com/lepture/authlib"""
        rand = SystemRandom()
        return ''.join(rand.choice(string.ascii_letters + string.digits) for _ in range(48))

    def _auth0_authorize(self):
        """
        1. /autorize
        Get Auth0 config
        """
        self.code_verifier = self._generate_token()
        endpoint = 'https://ru.accounts.ikea.com/authorize'
        params = {
            'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
            'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
            'response_type': 'code',
            'ui_locales': 'ru-RU',
            'code_chalenge': self._create_s256_code_challenge(self.code_verifier),
            'code_chalenge_method': 'S256',
            'scope': 'openid profile email',
            'audience': 'https://retail.api.ikea.com',
            'registration': '{"bveventid":null}',
            'consumer': 'OWF',
            'state': self._generate_token(),
            'auth0Client': 'eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0='
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.',
            'Referer': 'https://www.ikea.com/ru/ru/profile/login/'
        }
        response = self.session.get(
            endpoint, params=params, headers=headers)
        check_response(response)

        encoded_config = BeautifulSoup(response.text, 'html.parser').find(
            'script', id='a0-config').get('data-config')
        session_config = json.loads(b64decode(encoded_config))
        return {'session_config': session_config, 'url': response.url}

    def _usernamepassword_login(self, usr, pwd, session_config, authorize_final_url):
        """
        2. /usernamepassword/login
        Log in and get wctx and wresult params
        """
        endpoint = 'https://ru.accounts.ikea.com/usernamepassword/login'
        payload = {
            'state': session_config['extraParams']['state'],
            '_csrf': session_config['extraParams']['_csrf'],
            'response_type': session_config['extraParams']['response_type'],
            'scope': session_config['extraParams']['scope'],
            'audience': session_config['extraParams']['audience'],
            'tenant': session_config['auth0Tenant'],
            'password': pwd,
            'redirect_uri': session_config['callbackURL'],
            '_intstate': session_config['extraParams']['_intstate'],
            'client_id': session_config['clientID'],
            'username': usr,
            'connection': 'Username-Password-Authentication'
        }
        headers = {
            'Accept': '*/*',
            'Referer': authorize_final_url,
            'Auth0-Client': session_config['extraParams']['auth0Client'],
            'Origin': 'https://ru.accounts.ikea.com'
        }
        response = self.session.post(
            endpoint, headers=headers, json=payload)
        check_response(response)

        soup = BeautifulSoup(response.text, 'html.parser')
        wctx = soup.find('input', {'name': 'wctx'}).get('value')
        wresult = soup.find('input', {'name': 'wresult'}).get('value')
        return {'wctx': wctx, 'wresult': wresult, 'url': response.url}

    def _login_callback(self, wctx, wresult, usernamepassword_login_final_url):
        """
        3. /login/callback
        Get code parameter from callback
        """
        endpoint = 'https://ru.accounts.ikea.com/login/callback'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Origin': 'https://ru.accounts.ikea.com',
            'Referer': usernamepassword_login_final_url
        }
        payload = {
            'wa': 'wsignin1.0',
            'wresult': wresult,
            'wctx': wctx
        }
        response = self.session.post(
            endpoint, headers=headers, data=payload)
        check_response(response)

        code = parse_qs(urlparse(response.url).query)['code'][0]
        return {'code': code, 'url': response.url}

    def _oauth_token(self, callback_code, callback_final_url):
        """
        4. /oauth/token
        Get access token
        """
        endpoint = 'https://ru.accounts.ikea.com/oauth/token'
        headers = {
            'Accept': '*/*',
            'Referer': callback_final_url,
            'Origin': 'https://www.ikea.com'
        }
        payload = {
            'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
            'code_verifier': self.code_verifier,
            'code': callback_code,
            'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
            'scope': 'openid profile email',
            'grant_type': 'authorization_code'
        }
        response = self.session.post(endpoint, headers=headers, json=payload)
        check_response(response)

        token = response.json()['access_token']
        return token
