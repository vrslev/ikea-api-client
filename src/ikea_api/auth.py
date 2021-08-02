from typing import Any, Dict, Optional

from .constants import Constants
from .errors import InvalidRetailUnitError, UnauthorizedError
from .utils import check_response

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


# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false


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
    payload = {"retailUnit": Constants.LANGUAGE_CODE}
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
    Required IKEA added complicated telemetry. Old implementaion:
    https://github.com/vrslev/ikea-api-client/blob/39fe5210305e28efd8f434dde4bfeb9881872d42/ikea_api/auth.py)

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
        password_el.click()
        password_el.send_keys(self.password)
        password_el.send_keys(Keys.ENTER)

        self._cookie: Optional[Dict[str, Any]] = None
        for i in range(10):  # type: ignore
            self._cookie = self._driver.get_cookie("idp_reguser")
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
