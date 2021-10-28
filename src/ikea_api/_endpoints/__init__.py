from __future__ import annotations

from ikea_api._endpoints.auth import get_authorized_token, get_guest_token
from ikea_api._endpoints.cart import Cart
from ikea_api._endpoints.item import parse_item_code
from ikea_api._endpoints.item.item_ingka import fetch as _fetch_items_specs_ingka
from ikea_api._endpoints.item.item_iows import fetch as _fetch_items_specs_iows
from ikea_api._endpoints.item_pip import ItemPip
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
    def pip(items: list[str]):
        item_codes = parse_item_code(items)
        item = ItemPip()
        return [item(item_code) for item_code in item_codes]


__all__ = [
    "Cart",
    "OrderCapture",
    "Purchases",
    "Items",
    "Search",
    "get_guest_token",
    "get_authorized_token",
]
