from copy import copy
from typing import Any

import pytest
import responses

import ikea_api._endpoints.order_capture
from ikea_api._constants import Constants, Secrets
from ikea_api._endpoints.cart import Cart
from ikea_api._endpoints.order_capture import (
    OrderCapture,
    _validate_state_code,
    _validate_zip_code,
)
from ikea_api.exceptions import NoDeliveryOptionsAvailableError, OrderCaptureError


@pytest.fixture
def order_capture():
    return ikea_api._endpoints.order_capture.OrderCapture(
        "some value", zip_code="101000"
    )


@pytest.mark.parametrize(
    "v",
    (
        {"data": {}},
        {"data": {"cart": {}}},
        {"data": {"cart": {"items": []}}},
        {"data": {"cart": {"items": None}}},
    ),
)
def test_get_items_for_checkout_failes(
    monkeypatch: pytest.MonkeyPatch, order_capture: OrderCapture, v: dict[str, Any]
):
    class CustomCart(Cart):
        def show(self):  # type: ignore
            return v

    monkeypatch.setattr(ikea_api._endpoints.order_capture, "Cart", CustomCart)
    with pytest.raises(RuntimeError, match="Cannot get items for Order Capture"):
        order_capture._get_items_for_checkout()


@responses.activate
def test_get_checkout_failes(order_capture: OrderCapture):
    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts",
        json={"not resourceId": "bar"},
    )
    with pytest.raises(RuntimeError, match="No resourceId for checkout"):
        order_capture._get_checkout([])


@responses.activate
def test_get_delivery_area_failes(order_capture: OrderCapture):
    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas",
        json={"not resourceId": "bar"},
    )
    with pytest.raises(RuntimeError, match="No resourceId for delivery area"):
        order_capture._get_delivery_area("mycheckout")


@pytest.mark.parametrize("with_state_code", (True, False))
@responses.activate
def test_get_delivery_area_data(order_capture: OrderCapture, with_state_code: bool):
    order_capture._zip_code = "1000"
    exp_data = {"enableRangeOfDays": False, "zipCode": "1000"}
    if with_state_code:
        order_capture._state_code = "LA"
        exp_data["stateCode"] = "LA"
    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas",
        json={"resourceId": "bar"},
        match=[responses.matchers.json_params_matcher(exp_data)],  # type: ignore
    )
    order_capture._get_delivery_area("mycheckout")


@pytest.mark.parametrize("code", (60005, 60006))
@responses.activate
def test_get_delivery_services_fails_known_err(order_capture: OrderCapture, code: int):
    responses.add(
        responses.GET,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas/myarea/delivery-services",
        json={"errorCode": code},
    )
    with pytest.raises(NoDeliveryOptionsAvailableError):
        order_capture._get_delivery_services("mycheckout", "myarea")


@responses.activate
def test_get_delivery_services_fails_unknown_err(order_capture: OrderCapture):
    responses.add(
        responses.GET,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas/myarea/delivery-services",
        json={"errorCode": 60000},
    )
    with pytest.raises(OrderCaptureError):
        order_capture._get_delivery_services("mycheckout", "myarea")


@responses.activate
def test_order_capture_main(
    monkeypatch: pytest.MonkeyPatch, order_capture: OrderCapture
):
    exp_items = [
        {"quantity": 1, "itemNo": "11111111", "uom": "uom"},
        {"quantity": 4, "itemNo": "22222222", "uom": "uom"},
    ]

    class CustomCart(Cart):
        def show(self):  # type: ignore
            items = [
                {
                    "quantity": i["quantity"],
                    "itemNo": i["itemNo"],
                    "product": {"unitCode": i["uom"]},
                }
                for i in exp_items
            ]
            return {"data": {"cart": {"items": items}}}

    monkeypatch.setattr(ikea_api._endpoints.order_capture, "Cart", CustomCart)

    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts",
        json={"resourceId": "mycheckout"},
        match=[
            responses.matchers.header_matcher(  # type: ignore
                {"X-Client-Id": Secrets.order_capture_checkout_x_client_id}
            ),
            responses.matchers.json_params_matcher(  # type: ignore
                {
                    "channel": "WEBAPP",
                    "checkoutType": "STANDARD",
                    "shoppingType": "ONLINE",
                    "deliveryArea": None,
                    "items": exp_items,
                    "languageCode": Constants.LANGUAGE_CODE,
                }
            ),
        ],
    )

    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas",
        json={"resourceId": "myarea"},
        match=[
            responses.matchers.json_params_matcher(  # type: ignore
                {"enableRangeOfDays": False, "zipCode": copy(order_capture._zip_code)}
            )
        ],
    )

    responses.add(
        responses.GET,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/delivery-areas/myarea/delivery-services",
        json={"foo": "bar"},
    )

    assert order_capture() == {"foo": "bar"}


@pytest.mark.parametrize("v", ("100000", "2184011", "101000"))
def test_validate_zip_code_passes(v: str):
    _validate_zip_code(v)


@pytest.mark.parametrize("v", ("100.0.00", " 2184011", "10 1 0-00"))
def test_validate_zip_code_fails(v: str):
    with pytest.raises(ValueError, match=f"Invalid zip code: {v}"):
        _validate_zip_code(v)


@pytest.mark.parametrize("v", (None, "SA", "PO", "po", "sa"))
def test_validate_state_code_passes(v: str | None):
    _validate_state_code(v)


@pytest.mark.parametrize("v", ("Saa", "Русский", "other values", "  ", "--"))
def test_validate_state_code_failes(v: str):
    with pytest.raises(ValueError, match=f"Invalid state code: {v}"):
        _validate_state_code(v)
