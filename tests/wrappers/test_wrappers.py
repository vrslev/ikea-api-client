from typing import Callable

import pytest

import ikea_api.executors.httpx
import ikea_api.executors.requests
import ikea_api.wrappers.wrappers
from ikea_api.abc import RequestInfo, ResponseInfo
from ikea_api.constants import Constants
from ikea_api.endpoints import cart, purchases
from ikea_api.endpoints.cart import convert_items
from ikea_api.endpoints.order_capture import convert_cart_to_checkout_items
from ikea_api.executors.httpx import HttpxExecutor
from ikea_api.executors.requests import RequestsExecutor
from ikea_api.wrappers import types
from ikea_api.wrappers.wrappers import (
    add_items_to_cart,
    get_delivery_services,
    get_purchase_history,
    get_purchase_info,
)
from tests.conftest import MockResponseInfo, TestData


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
    api = purchases.API(constants, token="mytoken")  # nosec
    patch_requests_executor(
        monkeypatch, lambda _: MockResponseInfo(json_=TestData.purchases_history)
    )
    res = get_purchase_history(api)
    assert isinstance(res[0], types.PurchaseHistoryItem)


def test_get_purchase_info(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    api = purchases.API(constants, token="mytoken")  # nosec
    patch_requests_executor(
        monkeypatch,
        lambda _: MockResponseInfo(
            json_=[TestData.purchases_status_banner, TestData.purchases_costs]
        ),
    )
    res = get_purchase_info(api, order_number="1")
    assert isinstance(res, types.PurchaseInfo)


def test_add_items_to_cart(monkeypatch: pytest.MonkeyPatch, constants: Constants):
    api = cart.API(constants, token="mytoken")  # nosec
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
