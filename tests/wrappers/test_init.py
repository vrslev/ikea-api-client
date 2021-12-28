from __future__ import annotations

import re
import sys
from copy import copy, deepcopy
from types import SimpleNamespace
from typing import Any

import pytest

import ikea_api._endpoints.item_iows
import ikea_api.wrappers
from ikea_api import IKEA
from ikea_api._api import GraphQLResponse
from ikea_api._endpoints.order_capture import OrderCapture
from ikea_api.exceptions import GraphQLError, ItemFetchError
from ikea_api.wrappers import (
    _get_pip_items_map,
    _split_to_chunks,
    add_items_to_cart,
    get_purchase_history,
    get_purchase_info,
    types,
)
from ikea_api.wrappers._parsers import item_ingka, item_iows, item_pip
from tests.wrappers._parsers.test_item_ingka import test_data as mock_ingka_items
from tests.wrappers._parsers.test_item_iows import test_data as mock_iows_items
from tests.wrappers._parsers.test_item_pip import test_data as mock_pip_items
from tests.wrappers._parsers.test_order_capture import (
    test_collect_delivery_services_data,
    test_home_delivery_services_data,
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

    class CustomIKEA:
        @property
        def purchases(self):
            return CustomPurchases()

    called_parse = False

    def mock_parse_history(response: GraphQLResponse):
        assert response == mock_history
        nonlocal called_parse
        called_parse = True

    monkeypatch.setattr(
        ikea_api.wrappers.purchases, "parse_history", mock_parse_history
    )
    get_purchase_history(CustomIKEA())  # type: ignore
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

    class CustomIKEA:
        @property
        def purchases(self):
            return CustomPurchases()

    called_parse_status_banner = False
    old_parse_status_banner = ikea_api.wrappers.purchases.parse_status_banner_order

    def mock_parse_status_banner_order(response: GraphQLResponse):
        nonlocal called_parse_status_banner
        called_parse_status_banner = True
        assert response == mock_status_banner
        return old_parse_status_banner(response)

    called_parse_costs = False
    old_parse_costs = ikea_api.wrappers.purchases.parse_costs_order

    def mock_parse_costs_order(response: GraphQLResponse):
        nonlocal called_parse_costs
        called_parse_costs = True
        assert response == mock_costs
        return old_parse_costs(response)

    monkeypatch.setattr(
        ikea_api.wrappers.purchases,
        "parse_status_banner_order",
        mock_parse_status_banner_order,
    )
    monkeypatch.setattr(
        ikea_api.wrappers.purchases, "parse_costs_order", mock_parse_costs_order
    )

    res = get_purchase_info(CustomIKEA(), id=exp_id, email=exp_email)  # type: ignore
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

    class CustomIKEA:
        @property
        def cart(self):
            return CustomCart()

    res = add_items_to_cart(CustomIKEA(), items=exp_items.copy())  # type: ignore
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
                                {"extensions": {"code": "INVALID_ITEM_NUMBER"}},
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

    class CustomIKEA:
        @property
        def cart(self):
            if not hasattr(self, "_cart"):
                self._cart = CustomCart()
            return self._cart

    res = add_items_to_cart(CustomIKEA(), items=exp_items_first.copy())  # type: ignore
    assert called_clear
    assert called_add_items
    assert res == ["22222222", "33333333"]


def test_get_delivery_services_cannot_add_all_items(monkeypatch: pytest.MonkeyPatch):
    api_ = IKEA()
    exp_items = {"11111111": 2}
    exp_cannot_add = ["11111111"]
    called_add_items_to_cart = False

    def mock_add_items_to_cart(api: IKEA, items: dict[str, int]):
        nonlocal called_add_items_to_cart
        called_add_items_to_cart = True
        assert api == api_
        assert items == exp_items
        return exp_cannot_add

    monkeypatch.setattr(ikea_api.wrappers, "add_items_to_cart", mock_add_items_to_cart)

    res = ikea_api.wrappers.get_delivery_services(
        api_, items=exp_items.copy(), zip_code="101000"
    )
    assert called_add_items_to_cart
    assert res == types.GetDeliveryServicesResponse(
        delivery_options=[], cannot_add=exp_cannot_add
    )


@pytest.mark.parametrize("home", test_home_delivery_services_data)
@pytest.mark.parametrize("collect", test_collect_delivery_services_data)
def test_get_delivery_services_passes(
    monkeypatch: pytest.MonkeyPatch,
    home: dict[str, Any],
    collect: dict[str, Any],
):
    exp_zip_code = "101000"
    exp_items = {"11111111": 2, "22222222": 1}
    exp_cannot_add = ["11111111"]

    called_order_capture = False
    called_add_items_to_cart = False

    class MockOrderCapture(OrderCapture):
        def __init__(self, token: str, *, zip_code: str, state_code: str | None = None):
            nonlocal called_order_capture
            called_order_capture = True
            assert zip_code == exp_zip_code
            assert state_code is None
            super().__init__(token, zip_code=zip_code, state_code=state_code)

        def _get_items_for_checkout(self) -> list[dict[str, str | int]]:
            return []

        def _get_checkout(self, items: list[dict[str, str | int]]) -> str:
            return "mycheckout"

        def _get_service_area(self, checkout: str) -> str:
            return "mycheckout"

        def get_home_delivery_services(
            self, checkout_and_service_area: tuple[str, str] | None = None
        ) -> dict[str, Any]:
            return home

        def get_collect_delivery_services(
            self, checkout_and_service_area: tuple[str, str] | None = None
        ) -> dict[str, Any]:
            return collect

    def mock_add_items_to_cart(api: IKEA, items: dict[str, int]):
        nonlocal called_add_items_to_cart
        called_add_items_to_cart = True
        assert items == exp_items
        return exp_cannot_add

    monkeypatch.setattr(ikea_api.wrappers, "add_items_to_cart", mock_add_items_to_cart)
    monkeypatch.setattr(ikea_api, "OrderCapture", MockOrderCapture)

    res = ikea_api.wrappers.get_delivery_services(
        IKEA("mytoken"), items=exp_items.copy(), zip_code=exp_zip_code
    )
    assert called_order_capture
    assert called_add_items_to_cart
    assert res.cannot_add == exp_cannot_add


@pytest.mark.parametrize(
    ("list_", "chunk_size", "expected"),
    (
        (["11111111"] * 50, 26, [["11111111"] * 26, ["11111111"] * 24]),
        (["11111111"] * 75, 80, [["11111111"] * 75]),
        (["11111111"] * 10, 5, [["11111111"] * 5, ["11111111"] * 5]),
        (
            ["11111111", "11111111", "22222222", "33333333"],
            2,
            [["11111111", "11111111"], ["22222222", "33333333"]],
        ),
    ),
)
def test_split_to_chunks(list_: list[str], chunk_size: int, expected: list[list[str]]):
    result = list(_split_to_chunks(list_, chunk_size))
    for res, exp in zip(result, expected):
        assert len(res) == len(exp)


@pytest.mark.parametrize("raise_handleable_exc", (True, False))
def test_get_iows_items_passes(
    monkeypatch: pytest.MonkeyPatch, raise_handleable_exc: bool
):
    called_split_to_chunks = False
    called_fetcher = False
    called_parser = False

    def mock_split_to_chunks(list_: list[Any], chunk_size: int):
        nonlocal called_split_to_chunks
        called_split_to_chunks = True
        return _split_to_chunks(list_, chunk_size)

    class CustomFetcher:
        def __call__(self, item_codes: list[str]):
            assert all(i in ("11111111", "22222222") for i in item_codes)
            nonlocal called_fetcher
            called_fetcher = True
            if raise_handleable_exc and "22222222" in item_codes:
                raise ItemFetchError(SimpleNamespace(), "Wrong Item Code")  # type: ignore
            return [i["response"] for i in mock_iows_items]

    class CustomParser:
        @staticmethod
        def main(response: dict[str, Any]):
            nonlocal called_parser
            called_parser = True
            return item_iows.main(response)

    monkeypatch.setattr(ikea_api.wrappers, "_split_to_chunks", mock_split_to_chunks)
    monkeypatch.setattr(ikea_api.wrappers, "IowsItems", CustomFetcher)
    monkeypatch.setattr(ikea_api.wrappers, "item_iows", CustomParser)

    ikea_api.wrappers._get_iows_items(["11111111"] * 90 + ["22222222"] * 90)
    assert called_split_to_chunks
    assert called_fetcher
    assert called_parser


def test_get_iows_items_raises(monkeypatch: pytest.MonkeyPatch):
    called_fetcher = False
    exp_msg = "Some other error"

    class CustomFetcher:
        def __call__(self, item_codes: list[str]):
            nonlocal called_fetcher
            called_fetcher = True
            raise ItemFetchError(SimpleNamespace(), copy(exp_msg))  # type: ignore

    monkeypatch.setattr(ikea_api.wrappers, "IowsItems", CustomFetcher)

    with pytest.raises(ItemFetchError, match=exp_msg):
        assert ikea_api.wrappers._get_iows_items(["11111111"]) == []
    assert called_fetcher


def test_get_ingka_items(monkeypatch: pytest.MonkeyPatch):
    called_split_to_chunks = False
    called_fetcher = False
    called_parser = False
    exp_item_codes = ["11111111"]

    def mock_split_to_chunks(list_: list[Any], chunk_size: int):
        nonlocal called_split_to_chunks
        called_split_to_chunks = True
        return _split_to_chunks(list_, chunk_size)

    class CustomFetcher:
        def __call__(self, item_codes: list[str]):
            assert item_codes == exp_item_codes
            nonlocal called_fetcher
            called_fetcher = True
            return deepcopy(mock_ingka_items[0]["response"])

    class CustomParser:
        @staticmethod
        def main(response: dict[str, Any]):
            nonlocal called_parser
            called_parser = True
            return item_ingka.main(response)

    monkeypatch.setattr(ikea_api.wrappers, "_split_to_chunks", mock_split_to_chunks)
    monkeypatch.setattr(ikea_api.wrappers, "IngkaItems", CustomFetcher)
    monkeypatch.setattr(ikea_api.wrappers, "item_ingka", CustomParser)

    res = ikea_api.wrappers._get_ingka_items(deepcopy(exp_item_codes))
    assert called_split_to_chunks
    assert called_fetcher
    assert called_parser
    assert len(res) == 1


def test_get_pip_items(monkeypatch: pytest.MonkeyPatch):
    called_fetcher = False
    called_parser = False
    exp_item_codes = ["11111111", "22222222"]

    class CustomFetcher:
        def __call__(self, item_code: str):
            assert item_code in exp_item_codes
            nonlocal called_fetcher
            called_fetcher = True
            return deepcopy(mock_pip_items[0]["response"])

    class CustomParser:
        @staticmethod
        def main(response: dict[str, Any]):
            nonlocal called_parser
            called_parser = True
            return item_pip.main(response)

    monkeypatch.setattr(ikea_api.wrappers, "PipItem", CustomFetcher)
    monkeypatch.setattr(ikea_api.wrappers, "item_pip", CustomParser)

    res = ikea_api.wrappers._get_pip_items(deepcopy(exp_item_codes))
    assert called_fetcher
    assert called_parser
    assert len(res) == 2


def test_get_pip_items_map():
    items = [
        SimpleNamespace(item_code="11111111"),
        SimpleNamespace(item_code="11111111", name="test"),
        SimpleNamespace(item_code="22222222"),
        None,
    ]
    res = _get_pip_items_map(items)  # type: ignore
    assert res["11111111"] == SimpleNamespace(item_code="11111111", name="test")
    assert res["22222222"] == SimpleNamespace(item_code="22222222")


def test_get_ingka_pip_items(monkeypatch: pytest.MonkeyPatch):
    exp_item_codes = ["11111111", "22222222", "33333333", "44444444"]

    def mock_get_ingka_items(item_codes: list[str]):
        assert item_codes == exp_item_codes
        return [
            types.IngkaItem(
                is_combination=False,
                item_code="11111111",
                name="first item",
                image_url="https://ikea.com/image1.jpg",
                weight=10.0,
                child_items=[],
            ),
            types.IngkaItem(
                is_combination=True,
                item_code="22222222",
                name="second item",
                image_url="https://ikea.com/image2.jpg",
                weight=21.0,
                child_items=[
                    types.ChildItem(
                        name="child item", item_code="12121212", weight=10.5, qty=2
                    )
                ],
            ),
            types.IngkaItem(
                is_combination=False,
                item_code="44444444",
                name="fourth item",
                image_url="https://ikea.com/image4.jpg",
                weight=0.55,
                child_items=[],
            ),
        ]

    def mock_get_pip_items(item_codes: list[str]):
        assert item_codes == exp_item_codes
        return [
            types.PipItem(
                item_code="11111111",
                price=1000,
                url="https://ikea.com/11111111",
                category_name="test category name",
                category_url="https://ikea.com/category/1",  # type: ignore
            ),
            types.PipItem(
                item_code="22222222",
                price=20000,
                url="https://ikea.com/22222222",
                category_name=None,
                category_url=None,
            ),
            types.PipItem(
                item_code="33333333",
                price=20000,
                url="https://ikea.com/33333333",
                category_name=None,
                category_url=None,
            ),
        ]

    monkeypatch.setattr(ikea_api.wrappers, "_get_ingka_items", mock_get_ingka_items)
    monkeypatch.setattr(ikea_api.wrappers, "_get_pip_items", mock_get_pip_items)
    res = ikea_api.wrappers._get_ingka_pip_items(deepcopy(exp_item_codes))
    assert res == [
        types.ParsedItem(
            is_combination=False,
            item_code="11111111",
            name="first item",
            image_url="https://ikea.com/image1.jpg",
            weight=10.0,
            child_items=[],
            price=1000,
            url="https://ikea.com/11111111",
            category_name="test category name",
            category_url="https://ikea.com/category/1",  # type: ignore
        ),
        types.ParsedItem(
            is_combination=True,
            item_code="22222222",
            name="second item",
            image_url="https://ikea.com/image2.jpg",
            weight=21.0,
            child_items=[
                types.ChildItem(
                    name="child item", item_code="12121212", weight=10.5, qty=2
                )
            ],
            price=20000,
            url="https://ikea.com/22222222",
            category_name=None,
            category_url=None,
        ),
    ]


def test_get_items_iows_fails(monkeypatch: pytest.MonkeyPatch):
    called_iows_fetcher = False
    called_ingka_pip_items = False
    exp_item_codes = ["11111111", "22222222"]
    exp_result = [SimpleNamespace(test="test")]

    class CustomIowsItems:
        def __call__(self, item_codes: list[str]):
            assert item_codes == exp_item_codes
            nonlocal called_iows_fetcher
            called_iows_fetcher = True
            raise ItemFetchError(SimpleNamespace(), "Wrong Item Code")  # type: ignore

    def mock_get_ingka_pip_items(item_codes: list[str]):
        assert item_codes == exp_item_codes
        nonlocal called_ingka_pip_items
        called_ingka_pip_items = True
        return exp_result

    monkeypatch.setattr(ikea_api.wrappers, "IowsItems", CustomIowsItems)
    monkeypatch.setattr(
        ikea_api.wrappers, "_get_ingka_pip_items", mock_get_ingka_pip_items
    )

    res = ikea_api.wrappers.get_items(deepcopy(exp_item_codes))
    assert called_iows_fetcher
    assert called_ingka_pip_items
    assert res == exp_result


def test_get_items_iows_gets_all_items(monkeypatch: pytest.MonkeyPatch):
    called_iows_fetcher = False
    exp_item_codes = ["11111111", "22222222"]
    exp_result = [
        SimpleNamespace(item_code="11111111"),
        SimpleNamespace(item_code="22222222"),
    ]

    def mock_get_iows_items(item_codes: list[str]):
        assert item_codes == exp_item_codes
        nonlocal called_iows_fetcher
        called_iows_fetcher = True
        return deepcopy(exp_result)

    def mock_get_ingka_pip_items(item_codes: list[str]):
        assert False, "_get_ingka_pip_items shouldn't be called"  # pragma: no cover

    monkeypatch.setattr(ikea_api.wrappers, "_get_iows_items", mock_get_iows_items)
    monkeypatch.setattr(
        ikea_api.wrappers, "_get_ingka_pip_items", mock_get_ingka_pip_items
    )
    res = ikea_api.wrappers.get_items(deepcopy(exp_item_codes))

    assert called_iows_fetcher
    assert res == exp_result


def test_get_items_main(monkeypatch: pytest.MonkeyPatch):
    called_iows_fetcher = False
    called_ingka_pip_items = False
    exp_item_codes = ["11111111", "22222222"]

    def mock_parse_item_codes(item_codes: list[str], unshorten_ingka_pagelinks: bool):
        assert item_codes == exp_item_codes
        assert unshorten_ingka_pagelinks is True
        return item_codes

    def mock_get_iows_items(item_codes: list[str]):
        assert item_codes == exp_item_codes
        nonlocal called_iows_fetcher
        called_iows_fetcher = True
        return [SimpleNamespace(item_code="11111111")]

    def mock_get_ingka_pip_items(item_codes: list[str]):
        assert item_codes == ["22222222"]
        nonlocal called_ingka_pip_items
        called_ingka_pip_items = True
        return [SimpleNamespace(item_code="22222222")]

    monkeypatch.setattr(ikea_api.wrappers, "parse_item_codes", mock_parse_item_codes)
    monkeypatch.setattr(ikea_api.wrappers, "_get_iows_items", mock_get_iows_items)
    monkeypatch.setattr(
        ikea_api.wrappers, "_get_ingka_pip_items", mock_get_ingka_pip_items
    )

    res = ikea_api.wrappers.get_items(deepcopy(exp_item_codes))
    assert called_iows_fetcher
    assert called_ingka_pip_items
    assert res == [
        SimpleNamespace(item_code="11111111"),
        SimpleNamespace(item_code="22222222"),
    ]
