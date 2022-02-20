from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any, Callable

import pytest

import ikea_api.executors.httpx
import ikea_api.executors.requests
import ikea_api.wrappers.wrappers
from ikea_api.abc import EndpointInfo, RequestInfo, ResponseInfo
from ikea_api.constants import Constants
from ikea_api.endpoints import cart, purchases
from ikea_api.endpoints.cart import convert_items
from ikea_api.endpoints.order_capture import convert_cart_to_checkout_items
from ikea_api.executors.httpx import HttpxExecutor
from ikea_api.executors.requests import RequestsExecutor
from ikea_api.utils import parse_item_codes
from ikea_api.wrappers import types
from ikea_api.wrappers.wrappers import (
    _get_ingka_items,
    _get_ingka_pip_items,
    _get_iows_items,
    _get_pip_items,
    _get_pip_items_map,
    add_items_to_cart,
    chunks,
    get_delivery_services,
    get_items,
    get_purchase_history,
    get_purchase_info,
)
from tests.conftest import MockResponseInfo, TestData


def test_pydantic_import_fails():
    sys.modules["pydantic"] = None  # type: ignore
    del sys.modules["ikea_api.wrappers.wrappers"]
    with pytest.raises(
        RuntimeError, match="To use wrappers you need Pydantic to be installed"
    ):
        import ikea_api.wrappers.wrappers  # type: ignore
    del sys.modules["pydantic"]


def patch_requests_executor(
    m: pytest.MonkeyPatch, func: Callable[[RequestInfo], ResponseInfo]
):
    class PatchedRequestsExecutor(RequestsExecutor):
        @staticmethod
        def request(request: RequestInfo) -> ResponseInfo:  # type: ignore
            return func(request)

    m.setattr(ikea_api.executors.requests, "RequestsExecutor", PatchedRequestsExecutor)


def patch_httpx_executor(
    m: pytest.MonkeyPatch, func: Callable[[RequestInfo], ResponseInfo]
):
    class PatchedHttpxExecutor(HttpxExecutor):
        @staticmethod
        async def request(request: RequestInfo) -> ResponseInfo:  # type: ignore
            return func(request)

    m.setattr(ikea_api.executors.httpx, "HttpxExecutor", PatchedHttpxExecutor)


def test_get_purchase_history(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    api = purchases.Purchases(constants, token="mytoken")  # nosec
    patch_requests_executor(
        monkeypatch, lambda _: MockResponseInfo(json_=TestData.purchases_history)
    )
    res = get_purchase_history(api)
    assert isinstance(res[0], types.PurchaseHistoryItem)


def test_get_purchase_info(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    api = purchases.Purchases(constants, token="mytoken")  # nosec
    patch_requests_executor(
        monkeypatch,
        lambda _: MockResponseInfo(
            json_=[TestData.purchases_status_banner, TestData.purchases_costs]
        ),
    )
    res = get_purchase_info(api, order_number="1")
    assert isinstance(res, types.PurchaseInfo)


def test_add_items_to_cart(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    api = cart.Cart(constants, token="mytoken")  # nosec
    exp_items = [
        {"11111111": 2, "22222222": 1, "33333333": 4},
        {"11111111": 2, "33333333": 4},
        {"11111111": 2},
    ]
    count = 0
    responses = [
        {
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
        },
        {
            "errors": [
                {
                    "extensions": {
                        "code": "INVALID_ITEM_NUMBER",
                        "data": {"itemNos": ["33333333"]},
                    }
                }
            ]
        },
        {},
    ]

    def func(request: RequestInfo) -> MockResponseInfo:
        if "clear" in str(request.json):
            return MockResponseInfo(json_="{}")

        nonlocal count
        assert request.json["variables"]["items"] == convert_items(exp_items[count])
        res = responses[count]
        count += 1

        return MockResponseInfo(json_=res)

    patch_requests_executor(monkeypatch, func)
    assert add_items_to_cart(api, exp_items[0]) == ["22222222", "33333333"]
    assert count == 3


async def test_get_delivery_services_cannot_add_all_items(
    monkeypatch: pytest.MonkeyPatch, constants: Constants
):
    item_code = "11111111"
    responses = [
        {},
        {
            "errors": [
                {
                    "extensions": {
                        "code": "INVALID_ITEM_NUMBER",
                        "data": {"itemNos": [item_code]},
                    }
                }
            ]
        },
    ]
    count = 0

    def func(_: RequestInfo):
        nonlocal count
        r = MockResponseInfo(json_=responses[count])
        count += 1
        return r

    patch_requests_executor(monkeypatch, func)

    res = await get_delivery_services(
        constants, "mytoken", items={item_code: 2}, zip_code="101000"  # nosec
    )
    assert not res.delivery_options
    assert res.cannot_add == [item_code]


async def test_get_delivery_services_main(
    monkeypatch: pytest.MonkeyPatch, constants: Constants
):
    patch_requests_executor(monkeypatch, lambda _: MockResponseInfo(json_={}))
    checkout_id = "21"
    service_area_id = "3490"
    zip_code = "101000"
    cart_response = {
        "data": {
            "cart": {
                "items": [
                    {
                        "quantity": 1,
                        "itemNo": "11111111",
                        "product": {"unitCode": "uom"},
                    },
                    {
                        "quantity": 4,
                        "itemNo": "22222222",
                        "product": {"unitCode": "uom"},
                    },
                ]
            }
        }
    }

    def func(request: RequestInfo):
        if "Cart" in str(request.json):
            return cart_response
        if request.url == "/checkouts":
            assert request.json["items"] == convert_cart_to_checkout_items(
                cart_response
            )
            return {"resourceId": checkout_id}
        if request.url == f"/checkouts/{checkout_id}/service-area":
            assert request.json["zipCode"] == zip_code
            return {"id": service_area_id}
        if (
            request.url
            == f"/checkouts/{checkout_id}/service-area/{service_area_id}/home-delivery-services"
        ):
            return TestData.order_capture_home[0]
        if (
            request.url
            == f"/checkouts/{checkout_id}/service-area/{service_area_id}/collect-delivery-services"
        ):
            return TestData.order_capture_collect[0]
        raise NotImplementedError(request)

    patch_httpx_executor(monkeypatch, lambda r: MockResponseInfo(json_=func(r)))
    res = await get_delivery_services(
        constants, "mytoken", items={"11111111": 2}, zip_code="101000"  # nosec
    )
    assert isinstance(res, types.GetDeliveryServicesResponse)


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
    result = list(chunks(list_, chunk_size))
    for res, exp in zip(result, expected):
        assert len(res) == len(exp)


async def test_get_ingka_items(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    async def func(e: Any):
        return TestData.item_ingka[0]

    monkeypatch.setattr(ikea_api.wrappers.wrappers, "run_with_httpx", func)
    res = await _get_ingka_items(constants, ["11111111"] * 51)
    assert len(res) == 2
    assert isinstance(res[0], types.IngkaItem)


async def test_get_pip_items(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    async def func(e: Any):
        return TestData.item_pip[1]

    monkeypatch.setattr(ikea_api.wrappers.wrappers, "run_with_httpx", func)
    res = await _get_pip_items(constants, ["11111111"] * 10)
    assert len(res) == 10
    assert isinstance(res[0], types.PipItem)


def test_get_pip_items_map():
    items: list[Any] = [
        SimpleNamespace(item_code="11111111"),
        SimpleNamespace(item_code="11111111", name="test"),
        SimpleNamespace(item_code="22222222"),
        None,
    ]
    res = _get_pip_items_map(items)
    assert res["11111111"] == SimpleNamespace(item_code="11111111", name="test")
    assert res["22222222"] == SimpleNamespace(item_code="22222222")


async def test_get_ingka_pip_items(
    constants: Constants, monkeypatch: pytest.MonkeyPatch
):
    exp_item_codes = ["11111111", "22222222", "33333333", "44444444"]

    async def mock_get_ingka_items(constants: Constants, item_codes: list[str]):
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

    async def mock_get_pip_items(constants: Constants, item_codes: list[str]):
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

    monkeypatch.setattr(
        ikea_api.wrappers.wrappers, "_get_ingka_items", mock_get_ingka_items
    )
    monkeypatch.setattr(
        ikea_api.wrappers.wrappers, "_get_pip_items", mock_get_pip_items
    )

    assert await _get_ingka_pip_items(constants, exp_item_codes) == [
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


async def test_get_iows_items(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    async def func(e: EndpointInfo[Any]):
        return [TestData.item_iows[0]] * len(e.func.args[1])

    monkeypatch.setattr(ikea_api.wrappers.wrappers, "run_with_httpx", func)
    res = await _get_iows_items(constants, ["11111111"] * 99)
    assert len(res) == 99
    assert isinstance(res[0], types.ParsedItem)


@pytest.mark.parametrize("early_exit", (True, False))
async def test_get_items_main(
    monkeypatch: pytest.MonkeyPatch, constants: Constants, early_exit: bool
):
    raw_item_codes = ["111.111.11", "22222222"]
    exp_item_codes = parse_item_codes(raw_item_codes)
    exp_items = [
        SimpleNamespace(item_code="11111111"),
        SimpleNamespace(item_code="22222222"),
    ]

    async def mock_get_ingka_pip_items(constants: Constants, item_codes: list[str]):
        assert item_codes == exp_item_codes
        if early_exit:
            return exp_items
        else:
            return [exp_items[0]]

    async def mock_get_iows_items(constants: Constants, item_codes: list[str]):
        if early_exit:
            raise NotImplementedError
        assert item_codes == [exp_item_codes[1]]
        return [exp_items[1]]

    monkeypatch.setattr(
        ikea_api.wrappers.wrappers, "_get_ingka_pip_items", mock_get_ingka_pip_items
    )
    monkeypatch.setattr(
        ikea_api.wrappers.wrappers, "_get_iows_items", mock_get_iows_items
    )

    assert await get_items(constants, raw_item_codes) == exp_items
