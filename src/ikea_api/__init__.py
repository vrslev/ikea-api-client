from __future__ import annotations

from ikea_api._constants import Constants
from ikea_api._endpoints.auth import get_guest_token
from ikea_api._endpoints.cart import Cart
from ikea_api._endpoints.item_ingka import IngkaItems
from ikea_api._endpoints.item_iows import IowsItems
from ikea_api._endpoints.item_pip import PipItem
from ikea_api._endpoints.order_capture import OrderCapture
from ikea_api._endpoints.purchases import Purchases
from ikea_api._endpoints.search import Search, SearchType

__all__ = [
    "IKEA",
    "IngkaItems",
    "IowsItems",
    "PipItem",
]


class IKEA:
    token: str

    def __init__(
        self,
        token: str | None = None,
        *,
        country_code: str = "ru",
        language_code: str = "ru",
    ):
        self.token = token  # type: ignore
        Constants.COUNTRY_CODE = country_code
        Constants.LANGUAGE_CODE = language_code

    def login_as_guest(self):
        """Log in as guest. Token expires in 30 days."""
        self.token = get_guest_token()

    @property
    def cart(self):
        """Manage cart."""
        if not hasattr(self, "_cart"):
            self._cart = Cart(self.token)
        return self._cart

    def order_capture(self, *, zip_code: str, state_code: str | None = None):
        """Get available delivery services."""
        return OrderCapture(self.token, zip_code=zip_code, state_code=state_code)()

    @property
    def purchases(self):
        """Get information about your purchases."""
        if not hasattr(self, "_purchases"):
            self._purchases = Purchases(self.token)
        return self._purchases

    def search(
        self, query: str, *, limit: int = 24, types: list[SearchType] = ["PRODUCT"]
    ):
        """Search the IKEA product catalog by product name"""
        return Search()(query=query, limit=limit, types=types)
