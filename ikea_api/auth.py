from base64 import b64decode, urlsafe_b64encode
import json

from bs4 import BeautifulSoup  # pyright: reportMissingTypeStubs=false

from .constants import Constants
from .errors import (
    InvalidRetailUnitError,
    NotAuthenticatedError,
    UnauthorizedError,
)
from .utils import (
    check_response,
    get_client_id_from_login_page,
    get_config_values,
)


def get_guest_token() -> str:
    """Token expires in 30 days"""
    from requests import post

    url = "https://api.ingka.ikea.com/guest/token"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-us",
        "Origin": Constants.BASE_URL,
        "Referer": Constants.BASE_URL + "/",
        "Connection": "keep-alive",
        "User-Agent": Constants.USER_AGENT,
        "X-Client-Id": "e026b58d-dd69-425f-a67f-1e9a5087b87b",
        "X-Client-Secret": "cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB",
    }
    payload = {"retailUnit": get_config_values()["language_code"]}
    response = post(url, headers=headers, json=payload)
    if response.text == "Invalid retail unit.":
        raise InvalidRetailUnitError
    if response.status_code == 401:
        raise UnauthorizedError(response.json())
    check_response(response)
    token = response.json()["access_token"]
    return token


def get_authorized_token(username, password) -> str:
    """
    OAuth2 authorization
    Token expires in 24 hours
    """
    return Auth(username, password).token


class Auth:
    """
    OAuth2 authorization
    Token expires in 24 hours
    """

    def __init__(self, username, password):
        from requests import Session

        self.session = Session()
        self.session.headers.update(
            {
                "Accept-Language": "en-us",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "User-Agent": Constants.USER_AGENT,
            }
        )
        config = get_config_values()
        self.client_id = config["client_id"]
        self.country_code = config["country_code"]
        self.language_code = config["language_code"]
        try:
            auth0_authorize = self._auth0_authorize()
        except AttributeError:
            self.client_id = get_client_id_from_login_page(
                self.country_code, self.language_code
            )
            auth0_authorize = self._auth0_authorize()
        usernamepassword_login = self._usernamepassword_login(
            username, password, **auth0_authorize
        )
        login_callback = self._login_callback(**usernamepassword_login)
        self._oauth_token(**login_callback)

    def _auth0_authorize(self):
        """
        1. /autorize
        Get Auth0 config
        """
        self.code_verifier = self._generate_token()
        endpoint = f"https://{self.country_code}.accounts.ikea.com/authorize"
        self.main_url = "{}/{}/{}/profile/login/".format(
            Constants.BASE_URL, self.country_code, self.language_code
        )
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.main_url,
            "response_type": "code",
            "ui_locales": f"{self.language_code}-{self.country_code.upper()}",
            "code_chalenge": self._create_s256_code_challenge(),
            "code_chalenge_method": "S256",
            "scope": "openid profile email",
            "audience": "https://retail.api.ikea.com",
            "registration": '{"bveventid":null}',
            "consumer": "OWF",
            "state": self._generate_token(),
            "auth0Client": "eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0=",
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.",
            "Referer": self.main_url,
        }
        response = self.session.get(endpoint, params=params, headers=headers)
        check_response(response)

        BeautifulSoup(response.text, "html.parser").find("script", id="a0-config")
        encoded_config = (
            BeautifulSoup(response.text, "html.parser")
            .find("script", id="a0-config")
            .get("data-config")
        )  # pyright: reportOptionalMemberAccess=false
        session_config = json.loads(b64decode(encoded_config))
        return {"session_config": session_config, "authorize_final_url": response.url}

    def _usernamepassword_login(self, usr, pwd, session_config, authorize_final_url):
        """
        2. /usernamepassword/login
        Log in and get wctx and wresult params
        """
        base_url = f"https://{self.country_code.lower()}.accounts.ikea.com"
        endpoint = f"{base_url}/usernamepassword/login"
        payload = {
            "state": session_config["extraParams"]["state"],
            "_csrf": session_config["extraParams"]["_csrf"],
            "response_type": session_config["extraParams"]["response_type"],
            "scope": session_config["extraParams"]["scope"],
            "audience": session_config["extraParams"]["audience"],
            "tenant": session_config["auth0Tenant"],
            "password": pwd,
            "redirect_uri": session_config["callbackURL"],
            "_intstate": session_config["extraParams"]["_intstate"],
            "client_id": session_config["clientID"],
            "username": usr,
            "connection": "Username-Password-Authentication",
        }
        headers = {
            "Accept": "*/*",
            "Referer": authorize_final_url,
            "Auth0-Client": session_config["extraParams"]["auth0Client"],
            "Origin": base_url,
        }
        response = self.session.post(endpoint, headers=headers, json=payload)
        if response.status_code == 401:
            response_json = response.json()
            if "description" in response_json:
                raise NotAuthenticatedError(response_json["description"])
            else:
                raise NotAuthenticatedError
        check_response(response)
        soup = BeautifulSoup(response.text, "html.parser")
        wctx = soup.find("input", {"name": "wctx"}).get("value")
        wresult = soup.find("input", {"name": "wresult"}).get("value")
        return {
            "wctx": wctx,
            "wresult": wresult,
            "usernamepassword_login_final_url": response.url,
            "base_url": base_url,
        }

    def _login_callback(
        self, wctx, wresult, usernamepassword_login_final_url, base_url
    ):
        """
        3. /login/callback
        Get code parameter from callback
        """
        from urllib.parse import parse_qs, urlparse

        endpoint = f"{base_url}/login/callback"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Origin": base_url,
            "Referer": usernamepassword_login_final_url,
        }
        payload = {"wa": "wsignin1.0", "wresult": wresult, "wctx": wctx}
        response = self.session.post(endpoint, headers=headers, data=payload)
        check_response(response)

        code = parse_qs(urlparse(response.url).query)["code"][0]
        return {
            "callback_code": code,
            "callback_final_url": response.url,
            "base_url": base_url,
        }

    def _oauth_token(self, callback_code, callback_final_url, base_url):
        """
        4. /oauth/token
        Get access token
        """
        endpoint = f"{base_url}/oauth/token"
        headers = {
            "Accept": "*/*",
            "Referer": callback_final_url,
            "Origin": Constants.BASE_URL,
        }
        payload = {
            "client_id": self.client_id,
            "code_verifier": self.code_verifier,
            "code": callback_code,
            "redirect_uri": self.main_url,
            "scope": "openid profile email",
            "grant_type": "authorization_code",
        }
        response = self.session.post(endpoint, headers=headers, json=payload)
        check_response(response)

        self.token = response.json()["access_token"]
        self._decode_and_set_jwt()
        return self.token

    def _generate_token(self):
        """From https://github.com/lepture/authlib"""
        from random import SystemRandom
        from string import ascii_letters, digits

        rand = SystemRandom()
        return "".join(rand.choice(ascii_letters + digits) for _ in range(48))

    def _create_s256_code_challenge(self):
        """
        From https://github.com/lepture/authlib
        Create S256 code_challenge with the given code_verifier.
        """
        from hashlib import sha256

        data = sha256(bytes(self.code_verifier.encode("ascii", "strict"))).digest()
        return urlsafe_b64encode(data).rstrip(b"=").decode("utf-8", "strict")

    def _decode_and_set_jwt(self):
        from re import findall

        matches = findall(r"\.(.*)\.", self.token)
        if len(matches) != 1:
            pass
        payload = b64decode(matches[0])
        decoded = json.loads(payload)
        self.jwt = decoded
