from .cart import Cart
from .item.item_ingka import fetch as _fetch_items_specs_ingka
from .item.item_iows import fetch as _fetch_items_specs_iows
from .item.item_pip import fetch as _fetch_item_specs_pip
from .order_capture import OrderCapture
from .purchases import Purchases

class fetch_items_specs:
    # pyright: reportGeneralTypeIssues=false
    def ingka(self):
        return _fetch_items_specs_ingka(self)

    def iows(self):
        return _fetch_items_specs_iows(self)

    def pip(self):
        return _fetch_item_specs_pip(self)


__all__ = ["Cart", "OrderCapture", "Purchases", "fetch_items_specs"]
