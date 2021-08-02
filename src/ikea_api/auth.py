from typing import Any, Dict, Optional

from .constants import Constants, Secrets
from .errors import IkeaApiError, InvalidRetailUnitError, UnauthorizedError

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
    from requests import post

    response = post(
        url="https://api.ingka.ikea.com/guest/token",
        headers={
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-us",
            "Origin": Constants.BASE_URL,
            "Referer": Constants.BASE_URL + "/",
            "Connection": "keep-alive",
            "User-Agent": Constants.USER_AGENT,
            "X-Client-Id": Secrets.auth_guest_token_x_client_id,
            "X-Client-Secret": Secrets.auth_guest_token_x_client_secret,
        },
        json={"retailUnit": Constants.LANGUAGE_CODE},
    )

    if response.text == "Invalid retail unit.":
        raise InvalidRetailUnitError
    elif response.status_code == 401:
        raise UnauthorizedError(response.json())
    elif not response.ok:
        raise IkeaApiError(response.status_code, response.text)

    return response.json()["access_token"]


def get_authorized_token(username: str, password: str):
    return Auth()(username, password)


class Auth:
    """
    Authorization using Selenium.
    Required IKEA added complicated telemetry. Old implementaion:
    https://github.com/vrslev/ikea-api-client/blob/39fe5210305e28efd8f434dde4bfeb9881872d42/ikea_api/auth.py)
    """

    def __init__(self):
        if not _driver_packages_installed:
            raise RuntimeError(
                '"selenium" and "chromedriver_autoinstaller" packages are not'
                'installed. Run "pip install ikea_api[driver]" to proceed.'
            )

        self._install_driver()

        self._url = "https://www.ikea.com/ru/ru/profile/login/"
        self._user_agent = (  # Different user agent is required: it is Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        )

        self._create_driver()

    def _install_driver(self):
        chromedriver_autoinstaller.install()

    def _create_driver(self):  # and make it undetectable
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
