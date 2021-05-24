from .cart import Cart
from .purchases import Purchases
from .order_capture import OrderCapture
from .item.item_iows import fetch as _fetch_items_specs_iows
from .item.item_ingka import fetch as _fetch_items_specs_ingka
from .item.item_pip import fetch as _fetch_item_specs_pip


class fetch_items_specs:
    def ingka(items):
        return _fetch_items_specs_ingka(items)

    def iows(items):
        return _fetch_items_specs_iows(items)

    def pip(items):
        return _fetch_item_specs_pip(items)
