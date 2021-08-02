from typing import Any, Dict, Optional

from .constants import Constants
from .errors import InvalidRetailUnitError, UnauthorizedError
from .utils import check_response, get_config_values

# pyright: reportMissingImports=false

_driver_packages_installed = True
try:
    import chromedriver_autoinstaller
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    import time  # isort: skip
except ImportError:
    _driver_packages_installed = False


_old_auth_loaded = True
try:
    from bs4 import BeautifulSoup  # isort: skip
    from base64 import b64decode, urlsafe_b64encode
    import json

    from .errors import NotAuthenticatedError
    from .utils import get_client_id_from_login_page
except ImportError:
    _old_auth_loaded = False


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


def get_authorized_token(username: str, password: str):
    """
    Token expires in 24 hours
    """
    return Auth()(username, password)


class Auth:
    """
    Authorization using Selenium.
    Required since old class is deprecated (now it is `_OldAuth`)

    Token expires in 24 hours.
    """

    def __init__(self):
        if not _driver_packages_installed:
            raise RuntimeError(
                '"selenium" and "chromedriver_autoinstaller" packages are not'
                'installed. Run "pip install ikea_api[driver]" to proceed.'
            )

        self._install_driver()

        self._url = "https://www.ikea.com/ru/ru/profile/login/"
        self._user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        )

        self._create_driver()

    def _install_driver(self):
        chromedriver_autoinstaller.install()

    def _create_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=2560x1600")

        self._driver = webdriver.Chrome(options=options)
        self._driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": self._user_agent}
        )
        self._driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    chrome = { runtime: {} };
                    const originalQuery = navigator.permissions.query;
                    navigator.permissions.query = (parameters) =>
                    parameters.name === "notifications"
                        ? Promise.resolve({ state: Notification.permission })
                        : originalQuery(parameters);
                    navigator.plugins = [1, 2, 3, 4, 5];
                    navigator.languages = ["en-US", "en"];
            """
            },
        )

    def _get_cookie(self):
        self._driver.get(self._url)

        username_el = WebDriverWait(self._driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#username"))
        )
        username_el.click()
        username_el.send_keys(self.username)

        password_el = self._driver.find_element_by_css_selector("input#password")
        password_el.click()  # type: ignore
        password_el.send_keys(self.password)  # type: ignore
        password_el.send_keys(Keys.ENTER)  # type: ignore

        self._cookie: Optional[Dict[str, Any]] = None
        for i in range(10):  # type: ignore
            self._cookie = self._driver.get_cookie("idp_reguser")  # type: ignore
            if self._cookie:
                self._driver.close()
                break
            time.sleep(0.5)

    def _get_token(self):
        if self._cookie:
            self.token: Optional[str] = self._cookie.get("value")

    def __call__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._get_cookie()
        self._get_token()
        return self.token


def _old_get_authorized_token(username, password) -> str:  # type: ignore
    """
    OAuth2 authorization
    Token expires in 24 hours
    """
    return _OldAuth(username, password).token


class _OldAuth:
    """
    OAuth2 authorization
    Token expires in 24 hours

    v0.2.0. Deprecated due to really complicated telemetry that IKEA added.
          Use Auth instead. Keeping it in case something will change
    """

    def __init__(self, username, password):
        if not _old_auth_loaded:
            raise RuntimeError(
                '"bs4" package is not installed. ' 'Run "pip install bs4" to proceed.'
            )
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

        bs = BeautifulSoup(response.text, "html.parser").find("script", id="a0-config")
        encoded_config: str = bs.find("script", id="a0-config").get("data-config")  # type: ignore
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
        wctx = soup.find("input", {"name": "wctx"}).get("value")  # type: ignore
        wresult = soup.find("input", {"name": "wresult"}).get("value")  # type: ignore
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
