import re
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api._api import GraphQLResponse
from ikea_api.exceptions import GraphQLError
from ikea_api.wrappers import (
    add_items_to_cart,
    get_purchase_history,
    get_purchase_info,
    purchases,
    types,
)
from tests.wrappers._parsers.test_purchases import costs as mock_costs
from tests.wrappers._parsers.test_purchases import history as mock_history
from tests.wrappers._parsers.test_purchases import status_banner as mock_status_banner


def test_pydantic_import_passes():
    import ikea_api.wrappers  # type: ignore


def test_pydantic_import_fails():
    sys.modules["pydantic"] = None  # type: ignore
    del sys.modules["ikea_api.wrappers"]
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "To use wrappers you need Pydantic to be installed. "
            + "Run 'pip install \"ikea_api[wrappers]\"' to do so."
        ),
    ):
        import ikea_api.wrappers  # type: ignore
    del sys.modules["pydantic"]


def test_get_purchase_history(monkeypatch: pytest.MonkeyPatch):
    called_history = False

    class CustomPurchases:
        def history(self):
            nonlocal called_history
            called_history = True
            return mock_history

    class CustomIkeaApi:
        @property
        def purchases(self):
            return CustomPurchases()

    called_parse = False

    def mock_parse_history(response: GraphQLResponse):
        assert response == mock_history
        nonlocal called_parse
        called_parse = True

    monkeypatch.setattr(purchases, "parse_history", mock_parse_history)
    get_purchase_history(CustomIkeaApi())  # type: ignore
    assert called_history
    assert called_parse


@pytest.mark.parametrize("exp_email", ("me@example.com", None))
def test_get_purchase_info(monkeypatch: pytest.MonkeyPatch, exp_email: str | None):
    called_order_info = False
    exp_id = "11111111"

    class CustomPurchases:
        def order_info(self, order_number: str, email: str | None, queries: list[Any]):
            nonlocal called_order_info
            called_order_info = True
            assert order_number == exp_id
            assert email == exp_email
            assert queries == ["StatusBannerOrder", "CostsOrder"]
            return mock_status_banner, mock_costs

    class CustomIkeaApi:
        @property
        def purchases(self):
            return CustomPurchases()

    called_parse_status_banner = False
    old_parse_status_banner = purchases.parse_status_banner_order

    def mock_parse_status_banner_order(response: GraphQLResponse):
        nonlocal called_parse_status_banner
        called_parse_status_banner = True
        assert response == mock_status_banner
        return old_parse_status_banner(response)

    called_parse_costs = False
    old_parse_costs = purchases.parse_costs_order

    def mock_parse_costs_order(response: GraphQLResponse):
        nonlocal called_parse_costs
        called_parse_costs = True
        assert response == mock_costs
        return old_parse_costs(response)

    monkeypatch.setattr(
        purchases, "parse_status_banner_order", mock_parse_status_banner_order
    )
    monkeypatch.setattr(purchases, "parse_costs_order", mock_parse_costs_order)

    res = get_purchase_info(CustomIkeaApi(), exp_id, exp_email)  # type: ignore
    assert called_order_info
    assert called_parse_status_banner
    assert called_parse_costs
    assert isinstance(res, types.PurchaseInfo)


def test_add_items_to_cart_passes():
    called_clear = False
    called_add_items = False
    exp_items = {"11111111": 2}

    class CustomCart:
        def clear(self):
            nonlocal called_clear
            called_clear = True

        def add_items(self, items: dict[str, int]):
            nonlocal called_add_items
            called_add_items = True
            assert items == exp_items

    class CustomIkeaApi:
        @property
        def cart(self):
            return CustomCart()

    res = add_items_to_cart(CustomIkeaApi(), exp_items.copy())  # type: ignore
    assert called_clear
    assert called_add_items
    assert res == []


def test_add_items_to_cart_fails():
    called_clear = False
    called_add_items = False
    exp_items_first = {"11111111": 2, "22222222": 1, "33333333": 4}
    exp_items_second = {"11111111": 2, "33333333": 4}
    exp_items_third = {"11111111": 2}
    count = 0

    class CustomCart:
        def clear(self):
            nonlocal called_clear
            called_clear = True

        def add_items(self, items: dict[str, int]):
            nonlocal called_add_items
            called_add_items = True

            nonlocal count
            count += 1

            if count == 1:
                assert items == exp_items_first
                raise GraphQLError(
                    SimpleNamespace(  # type: ignore
                        _json={
                            "errors": [
                                {
                                    "extensions": {
                                        "code": "INVALID_ITEM_NUMBER",
                                        "data": {"itemNos": ["22222222"]},
                                    }
                                },
                                {
                                    "extensions": {
                                        "code": "not INVALID_ITEM_NUMBER",
                                        "data": {"itemNos": ["11111111"]},
                                    }
                                },
                            ]
                        }
                    )
                )
            elif count == 2:
                assert items == exp_items_second
                raise GraphQLError(
                    SimpleNamespace(  # type: ignore
                        _json={
                            "errors": [
                                {
                                    "extensions": {
                                        "code": "INVALID_ITEM_NUMBER",
                                        "data": {"itemNos": ["33333333"]},
                                    }
                                },
                            ]
                        }
                    )
                )
            elif count == 3:
                assert items == exp_items_third

    class CustomIkeaApi:
        @property
        def cart(self):
            if not hasattr(self, "_cart"):
                self._cart = CustomCart()
            return self._cart

    res = add_items_to_cart(CustomIkeaApi(), exp_items_first.copy())  # type: ignore
    assert called_clear
    assert called_add_items
    assert res == ["22222222", "33333333"]
