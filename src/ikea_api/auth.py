from __future__ import annotations

import asyncio
import os
import time

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

from ikea_api.api import API
from ikea_api.constants import Constants, Secrets


def get_guest_token():
    return GuestAuth().get_token()


class GuestAuth(API):
    def __init__(self):
        super().__init__(None, "https://api.ingka.ikea.com/guest/token")  # type: ignore
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": "en-us",
                "X-Client-Id": Secrets.auth_guest_token_x_client_id,
                "X-Client-Secret": Secrets.auth_guest_token_x_client_secret,
            }
        )

    def get_token(self) -> str:
        response: dict[str, str] = self._call_api(
            data={"retailUnit": Constants.LANGUAGE_CODE}
        )
        self._token = response["access_token"]
        return self._token


script = """
    chrome = { runtime: {} };
    const originalQuery = navigator.permissions.query;
    navigator.permissions.query = (parameters) =>
    parameters.name === "notifications"
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
    navigator.plugins = [1, 2, 3, 4, 5];
    navigator.languages = ["en-US", "en"];
"""


async def _get_driver():
    return await launch(
        args=[
            "--no-sandbox",
            "--window-position=0,0",
            '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 "
            'Safari/537.36"',
        ]
    )


# pyright: reportUnknownMemberType = false


async def _open_page(browser: Browser):
    page = await browser.newPage()
    await page.evaluateOnNewDocument(script)
    await page.goto(
        f"https://www.ikea.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/profile/login/"
    )
    return page


async def _get_token_from_cookie(page: Page):
    token: str | None = None
    for _ in range(200):
        cookies = await page.cookies()
        for cookie in cookies:
            if cookie["name"] == "idp_reguser":
                token = cookie["value"]  # type: ignore
        if token:
            break
        time.sleep(0.1)
    return token


async def _fill_form(page: Page, username: str, password: str):
    usr_el, pswd_el = "input#username", "input#password"
    await page.click(usr_el)
    await page.type(usr_el, username)
    await page.click(pswd_el)
    await page.type(pswd_el, password)
    await page.click("button[type=submit]")


async def _save_error_screenshot(page: Page):
    fpath = os.path.abspath("login_error_screenshot.png")
    await page.screenshot(path=fpath)
    raise RuntimeError(f"Cannot log in. Take look at the screenshot: {fpath}")


async def _main(username: str, password: str):
    browser = await _get_driver()
    page = await _open_page(browser)
    await _fill_form(page, username, password)
    token = await _get_token_from_cookie(page)
    await browser.close()
    if not token:
        return await _save_error_screenshot(page)
    return token


def get_authorized_token(username: str, password: str):
    return asyncio.get_event_loop().run_until_complete(_main(username, password))
