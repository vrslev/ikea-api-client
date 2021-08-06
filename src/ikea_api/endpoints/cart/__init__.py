from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from ikea_api.api import API
from ikea_api.constants import Constants, Secrets

from ..item import parse_item_code
from . import mutations, queries


def _build_payload_and_call(func: Callable[..., Any]):
    @wraps(func)
    def inner(self: Cart, *args: Any, **kwargs: Any):
        res: str | tuple[str] = func(self, *args, **kwargs)
        if isinstance(res, tuple):
            query, variables = res  # type: ignore
        else:
            query, variables = res, {}

        return self._call_api(data=self._build_payload(query, **variables))

    return inner


class Cart(API):
    def __init__(self, token: str):
        super().__init__(token, "https://cart.oneweb.ingka.com/graphql")
        self._session.headers["X-Client-Id"] = Secrets.cart_x_client_id

    def _build_payload(self, query: str, **variables: Any):
        payload = {
            "query": query,
            "variables": {"languageCode": Constants.LANGUAGE_CODE, **variables},
        }
        return payload

    def _make_templated_items(self, items: dict[str, int]):
        items_templated: list[dict[str, Any]] = []
        for item_code, qty in items.items():
            item_code = parse_item_code(item_code)
            if item_code:
                items_templated.append({"itemNo": item_code, "quantity": qty})
        return items_templated

    @_build_payload_and_call
    def show(self):
        return queries.cart

    @_build_payload_and_call
    def clear(self):
        return mutations.clear_items

    @_build_payload_and_call
    def add_items(self, items: dict[str, int]):
        """
        Add items to cart.
        Required items list format: {'item_no': quantity, ...}
        """
        items_templated = self._make_templated_items(items)
        return mutations.add_items, {"items": items_templated}

    @_build_payload_and_call
    def update_items(self, items: dict[str, int]):
        """
        Replace quantity for given item to the new one.
        Required items list format: {'item_no': quantity, ...}
        """
        items_templated = self._make_templated_items(items)
        return mutations.update_items, {"items": items_templated}

    @_build_payload_and_call
    def copy_items(self, source_user_id: str):
        """Copy cart from another account"""
        return mutations.copy_items, {"sourceUserId": source_user_id}

    @_build_payload_and_call
    def remove_items(self, item_codes: list[str]):
        """
        Remove items by item codes.
        """
        items_parsed = parse_item_code(item_codes)
        return mutations.remove_items, {"itemNos": items_parsed}

    @_build_payload_and_call
    def set_coupon(self, code: str):
        return mutations.set_coupon, {"code": code}

    @_build_payload_and_call
    def clear_coupon(self):
        return mutations.clear_coupon
