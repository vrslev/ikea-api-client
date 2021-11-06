from __future__ import annotations

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
            data={"retailUnit": Constants.COUNTRY_CODE}
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
