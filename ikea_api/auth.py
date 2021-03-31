import string
import re
import json
from random import SystemRandom
from base64 import urlsafe_b64encode, b64decode
from hashlib import sha256

from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

from .constants import Constants

class Auth():
    def __init__(self):
        self.base_headers = {
            'Accept-Encoding': Constants.ACCEPT_ENCODING,
            'Connection': 'keep-alive',
            'User-Agent': Constants.USER_AGENT
        }

    def get_guest_token(self):
        url = 'https://api.ingka.ikea.com/guest/token'
        headers = self.base_headers
        headers.update({
            'Accept-Language': 'ru',
            'Host': 'api.ingka.ikea.com',
            'X-Client-Id': 'e026b58d-dd69-425f-a67f-1e9a5087b87b',
            'X-Client-Secret': 'cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB',
            'Origin': 'https://www.ikea.com',
            'Referer': 'https://www.ikea.com/'
        })
        payload = {'retailUnit': 'ru'}
        response = requests.post(url, headers=headers,
                                 json=payload)
        token = response.json()['access_token']
        return token

    def create_s256_code_challenge(self, code_verifier):
        """
        https://github.com/lepture/authlib
        Create S256 code_challenge with the given code_verifier.
        """
        data = sha256(
            bytes(code_verifier.encode('ascii', 'strict'))).digest()
        return urlsafe_b64encode(data).rstrip(b'=').decode('utf-8', 'strict')

    def generate_token(self):
        """https://github.com/lepture/authlib"""
        rand = SystemRandom()
        return ''.join(rand.choice(string.ascii_letters + string.digits) for _ in range(48))

    def get_authorized_token(self, username, password):
        """OAuth2 authorization"""
        session = requests.Session()
        headers = self.base_headers
        headers['Accept-Language'] = 'en-us'

        # 1. /autorize  Autorize; redirects to /login with useful info
        code_verifier = self.generate_token()
        authorize_endpoint = 'https://ru.accounts.ikea.com/authorize?' + urlencode({
            'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
            'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
            'response_type': 'code',
            'ui_locales': 'ru-RU',
            'code_chalenge': self.create_s256_code_challenge(code_verifier),
            'code_chalenge_method': 'S256',
            'scope': 'openid profile email',
            'audience': 'https://retail.api.ikea.com',
            'registration': '{"bveventid":null}',
            'consumer': 'OWF',
            'state': self.generate_token(),
            'auth0Client': 'eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0='
        })
        authorize_headers = headers
        authorize_headers['Accept']: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
        authorize_response = session.get(
            authorize_endpoint, headers=authorize_headers)
        encoded_session_config = BeautifulSoup(authorize_response.text, 'html.parser').find(
            'script', id='a0-config').get('data-config')
        session_config = json.loads(b64decode(encoded_session_config))

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
        usrpwd_login_headers.update({
            'Referer': authorize_response.url,
            'Auth0-Client': session_config['extraParams']['auth0Client'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
        })
        usrpwd_login_result = session.post(
            usrpwd_login_endpoint, headers=usrpwd_login_headers, json=usrpwd_login_payload)
        if not usrpwd_login_result.ok:
            raise Exception(usrpwd_login_result.json())

        # 3. /login/callback    Get code parameter from callback
        soup = BeautifulSoup(usrpwd_login_result.text, 'html.parser')
        wctx = soup.find('input', {'name': 'wctx'}).get('value')
        wresult = soup.find('input', {'name': 'wresult'}).get('value')

        login_callback_endpoint = 'https://ru.accounts.ikea.com/login/callback'
        login_callback_headers = headers
        login_callback_headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ru.accounts.ikea.com',
            'Referer': usrpwd_login_result.url
        })
        login_callback_payload = 'wa=wsignin1.0&wresult=%s&wctx=%s' % (
            wresult, wctx)
        login_callback_response = session.post(
            login_callback_endpoint, headers=login_callback_headers, data=login_callback_payload)

        # 4. /oauth/token   Get access token
        oauth_token_enpoint = 'https://ru.accounts.ikea.com/oauth/token'
        oauth_token_headers = headers
        oauth_token_headers.update({
            'Content-Type': 'application/json',
            'Origin': 'https://www.ikea.com',
            'Accept-Encoding': 'gzip, deflate',  # TODO: Need to add 'br' encoding format
            'Accept': '*/*',
            'Referer': login_callback_response.url,
        })
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
