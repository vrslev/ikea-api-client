from __future__ import annotations

from ikea_api.endpoints.auth import get_authorized_token, get_guest_token
from ikea_api.endpoints.cart import Cart
from ikea_api.endpoints.item.item_ingka import fetch as _fetch_items_specs_ingka
from ikea_api.endpoints.item.item_iows import fetch as _fetch_items_specs_iows
from ikea_api.endpoints.item.item_pip import fetch as _fetch_items_specs_pip
from ikea_api.endpoints.order_capture import OrderCapture
from ikea_api.endpoints.purchases import Purchases


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
    "get_guest_token",
    "get_authorized_token",
]
