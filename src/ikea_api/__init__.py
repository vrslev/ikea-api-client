from __future__ import annotations

from ikea_api._endpoints import (
    Cart,
    Items,
    OrderCapture,
    Purchases,
    Search,
    get_authorized_token,
    get_guest_token,
)
from ikea_api._endpoints.search import SearchType
from ikea_api.constants import Constants

__version__ = "0.8.0"
__all__ = ["IkeaApi"]


class IkeaApi:
    _token: str

    def __init__(
        self,
        token: str | None = None,
        country_code: str = "ru",
        language_code: str = "ru",
    ):
        self._token = token  # type: ignore
        Constants.COUNTRY_CODE = country_code
        Constants.LANGUAGE_CODE = language_code

    def login(self, username: str, password: str):
        """Log in as registered user. Token expires in 24 hours.
        Since it uses Pyppeteer, it could take a while to proceed.
        """
        self._token = get_authorized_token(username, password)

    def login_as_guest(self):
        """Log in as guest. Token expires in 30 days."""
        self._token = get_guest_token()

    @property
    def cart(self):
        """Manage cart."""
        if not hasattr(self, "_cart"):
            self._cart = Cart(self._token)
        return self._cart

    def order_capture(self, zip_code: str, state_code: str | None = None):
        """Get available delivery services."""
        return OrderCapture(self._token, zip_code, state_code)()

    def search(
        self, query: str, limit: int = 24, types: list[SearchType] = ["PRODUCT"]
    ):
        """Search the IKEA product catalog by product name"""
        return Search()(query=query, limit=limit, types=types)

    @property
    def purchases(self):
        """Get information about your purchases."""
        if not hasattr(self, "_purchases"):
            self._purchases = Purchases(self._token)
        return self._purchases

    @property
    def items(self):
        """Get information about items."""
        if not hasattr(self, "_items"):
            self._items = Items
        return self._items
