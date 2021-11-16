from __future__ import annotations

import re
from typing import Any

from ikea_api.wrappers._parsers import get_box
from ikea_api.wrappers.types import PipItemDict

# pyright: reportUnknownMemberType=false


def parse_pip_item(dictionary: dict[str, Any]):
    return PipItem(dictionary)()


class PipItem:
    def __init__(self, dictionary: dict[str, Any]):
        self.d = get_box(dictionary)

    def get_item_code(self):
        item_code: str = self.d.id
        return re.sub("[^0-9]+", "", item_code)

    def get_price(self):
        price: Any = self.d.priceNumeral
        return int(price)

    def get_url(self):
        url: str = self.d.pipUrl
        return url

    def get_category_name_and_url(self) -> tuple[str | None, str | None]:
        categories: dict[Any, Any] = self.d.catalogRefs
        for _, ref in categories.items():
            if ref.elements[0].name and ref.elements[0].url:
                return ref.elements[0].name, ref.elements[0].url
        return None, None

    def __call__(self):
        category_name, category_url = self.get_category_name_and_url()
        return PipItemDict(
            item_code=self.get_item_code(),
            price=self.get_price(),
            url=self.get_url(),
            category_name=category_name,
            category_url=category_url,
        )
