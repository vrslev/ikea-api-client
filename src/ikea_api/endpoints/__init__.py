from __future__ import annotations

from .cart import Cart
from .item.item_ingka import fetch as _fetch_items_specs_ingka
from .item.item_iows import fetch as _fetch_items_specs_iows
from .item.item_pip import fetch as _fetch_items_specs_pip
from .order_capture import OrderCapture
from .purchases import Purchases


class fetch_items_specs:
    @staticmethod
    def ingka(items: str | list[str]):
        return _fetch_items_specs_ingka(items)

    @staticmethod
    def iows(items: str | list[str]):
        return _fetch_items_specs_iows(items)

    @staticmethod
    def pip(items: dict[str, bool]):
        return _fetch_items_specs_pip(items)


__all__ = ["Cart", "OrderCapture", "Purchases", "fetch_items_specs"]
