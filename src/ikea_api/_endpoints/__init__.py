from __future__ import annotations

from ikea_api._endpoints.auth import get_authorized_token, get_guest_token
from ikea_api._endpoints.cart import Cart
from ikea_api._endpoints.item.item_ingka import fetch as _fetch_items_specs_ingka
from ikea_api._endpoints.item.item_iows import fetch as _fetch_items_specs_iows
from ikea_api._endpoints.item.item_pip import fetch as _fetch_items_specs_pip
from ikea_api._endpoints.order_capture import OrderCapture
from ikea_api._endpoints.purchases import Purchases
from ikea_api._endpoints.search import Search


class Items:
    @staticmethod
    def ingka(items: str | list[str]):
        return _fetch_items_specs_ingka(items)

    @staticmethod
    def iows(items: str | list[str]):
        return _fetch_items_specs_iows(items)

    @staticmethod
    def pip(items: dict[str, bool]):
        return _fetch_items_specs_pip(items)


__all__ = [
    "Cart",
    "OrderCapture",
    "Purchases",
    "Items",
    "Search",
    "get_guest_token",
    "get_authorized_token",
]
