from __future__ import annotations

from typing import Any, Callable

import pytest

from ikea_api.constants import Constants
from ikea_api.endpoints.order_capture import (
    API,
    CheckoutItem,
    convert_cart_to_checkout_items,
)
from ikea_api.exceptions import ProcessingError
from tests.conftest import EndpointTester, MockResponseInfo


@pytest.fixture
def order_capture(constants: Constants):
    return API(constants, token="mytoken")  # nosec


@pytest.mark.parametrize("fail", (True, False))
def test_get_checkout(order_capture: API, fail: bool):
    items = [CheckoutItem(itemNo="11111111", quantity=1, uom="PIECE")]
    t = EndpointTester(order_capture.get_checkout(items))

    req = t.prepare()
    assert req.headers
    assert (
        req.headers["X-Client-Id"]
        != order_capture.get_session_info().headers["X-Client-Id"]
    )
    assert req.json["items"] == items
    assert req.json["languageCode"] == order_capture.const.language

    if fail:
        with pytest.raises(ProcessingError):
            t.parse(MockResponseInfo(json_={}))
    else:
        id = "myresource"
        assert t.parse(MockResponseInfo(json_={"resourceId": id})) == id


@pytest.mark.parametrize("state_code", (None, "mystate"))
def test_get_service_area_prepare(order_capture: API, state_code: str | None):
    checkout_id = "mycheckout"
    zip_code = "101000"
    t = EndpointTester(
        order_capture.get_service_area(checkout_id, zip_code, state_code)
    )

    req = t.prepare()
    assert req.url == f"/checkouts/{checkout_id}/service-area"

    payload = {"zipCode": zip_code}
    if state_code:
        payload["stateCode"] = state_code
    assert req.json == payload


@pytest.mark.parametrize("fail", (True, False))
def test_get_service_area_parse(order_capture: API, fail: bool):
    t = EndpointTester(order_capture.get_service_area("", ""))

    if fail:
        with pytest.raises(ProcessingError):
            t.parse(MockResponseInfo(json_={}))
    else:
        id = "myresource"
        assert t.parse(MockResponseInfo(json_={"id": id})) == id


@pytest.mark.parametrize(
    ("method", "path"),
    (
        (API.get_home_delivery_services, "home-delivery-services"),
        (API.get_collect_delivery_services, "collect-delivery-services"),
    ),
)
def test_get_services(order_capture: API, method: Callable[..., Any], path: str):
    checkout_id = "mycheckout"
    service_area_id = "myarea"

    t = EndpointTester(method(order_capture, checkout_id, service_area_id))
    req = t.prepare()

    assert req.url == f"/checkouts/{checkout_id}/service-area/{service_area_id}/{path}"

    t.assert_json_returned()


@pytest.mark.parametrize(
    "response",
    (
        {"data": {}},
        {"data": {"cart": {}}},
        {"data": {"cart": {"items": []}}},
        {"data": {"cart": {"items": None}}},
    ),
)
def test_convert_cart_to_checkout_items_fails(response: dict[str, Any]):
    with pytest.raises(RuntimeError):
        convert_cart_to_checkout_items(response)


def test_convert_cart_to_checkout_items_passes():
    out_items = [
        {"quantity": 1, "itemNo": "11111111", "uom": "uom"},
        {"quantity": 4, "itemNo": "22222222", "uom": "uom"},
    ]
    in_items = [
        {
            "quantity": i["quantity"],
            "itemNo": i["itemNo"],
            "product": {"unitCode": i["uom"]},
        }
        for i in out_items
    ]
    data = {"data": {"cart": {"items": in_items}}}
    assert convert_cart_to_checkout_items(data) == out_items
