from __future__ import annotations

from typing import Any

from ikea_api.constants import Constants
from ikea_api.endpoints.search import SearchTypes


class IkeaApi:
    def __init__(
        self,
        token: str | None = None,
        country_code: str = "ru",
        language_code: str = "ru",
    ):
        self._token_value = token

        Constants.COUNTRY_CODE, Constants.LANGUAGE_CODE = country_code, language_code

    def login(self, username: str, password: str):
        """
        Log in as registered user.
        Token expires in 24 hours.

        Since this method is using Selenium, you would have to wait up to 30 seconds.
        """

        from ikea_api.auth import get_authorized_token

        self._token = get_authorized_token(username, password)

    def login_as_guest(self):
        """Token expires in 30 days."""
        from ikea_api.auth import get_guest_token

        self._token = get_guest_token()

    def reveal_token(self):
        """Retrieve token."""
        return self._token_value

    @property
    def _token(self):
        if self._token_value is None:
            raise RuntimeError("No token provided")
        return self._token_value

    @_token.setter
    def _token(self, value: Any):
        self._token_value = value

    @property
    def Cart(self):
        """Manage cart."""
        if not hasattr(self, "_cart"):
            from ikea_api.endpoints import Cart

            self._cart = Cart(self._token)
        return self._cart

    def OrderCapture(self, zip_code: str, state_code: str | None = None):
        """Get available delivery services. Object is callable."""
        from ikea_api.endpoints import OrderCapture

        return OrderCapture(self._token, zip_code, state_code)()

    @property
    def Purchases(self):
        """Get information about your purchases."""
        if not hasattr(self, "_purchases"):
            from ikea_api.endpoints import Purchases

            self._purchases = Purchases(self._token)
        return self._purchases

    def Search(
        self, query: str, limit: int = 24, types: list[SearchTypes] = ["PRODUCT"]
    ):
        """Search the IKEA product catalog by product name"""
        from ikea_api.endpoints import Search

        return Search()(query=query, limit=limit, types=types)

    @property
    def fetch_items_specs(self):
        """Get information about items."""
        if not hasattr(self, "_fetch_items_specs"):
            from ikea_api.endpoints import fetch_items_specs

            self._fetch_items_specs = fetch_items_specs
        return self._fetch_items_specs
