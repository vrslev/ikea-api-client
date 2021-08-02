from .cart import Cart
from .item.item_ingka import fetch as _fetch_items_specs_ingka
from .item.item_iows import fetch as _fetch_items_specs_iows
from .item.item_pip import fetch as _fetch_item_specs_pip
from .order_capture import OrderCapture
from .purchases import Purchases


class _mock_fetch_items_specs:
    def __init__(self) -> None:
        self.ingka = _fetch_items_specs_ingka
        self.iows = _fetch_items_specs_iows
        self.pip = _fetch_item_specs_pip


fetch_items_specs = _mock_fetch_items_specs()

__all__ = ["Cart", "OrderCapture", "Purchases", "fetch_items_specs"]
