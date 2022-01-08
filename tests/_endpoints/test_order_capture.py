from __future__ import annotations

from copy import copy
from typing import Any, Callable

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
def test_get_service_area_failes(order_capture: OrderCapture):
    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/service-area",
        json={"not id": "bar"},
    )
    with pytest.raises(RuntimeError, match="No id for service area"):
        order_capture._get_service_area("mycheckout")


@pytest.mark.parametrize("with_state_code", (True, False))
@responses.activate
def test_get_service_area_data(order_capture: OrderCapture, with_state_code: bool):
    order_capture._zip_code = "1000"
    exp_data = {"zipCode": "1000"}
    if with_state_code:
        order_capture._state_code = "LA"
        exp_data["stateCode"] = "LA"
    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/service-area",
        json={"id": "bar"},
        match=[responses.matchers.json_params_matcher(exp_data)],  # type: ignore
    )
    assert order_capture._get_service_area("mycheckout") == "bar"


home_and_collect_method_and_endpoints = (
    ("method", "endpoint"),
    (
        (OrderCapture.get_home_delivery_services, "home-delivery-services"),
        (OrderCapture.get_collect_delivery_services, "collect-delivery-services"),
    ),
)


@pytest.mark.parametrize(*home_and_collect_method_and_endpoints)
@responses.activate
def test_order_capture_passes_with_checkout_and_service_area(
    order_capture: OrderCapture, method: Callable[..., Any], endpoint: str
):
    responses.add(
        responses.GET,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/service-area/myarea/{endpoint}",
        json={"foo": "bar"},
    )

    assert method(order_capture, ("mycheckout", "myarea")) == {"foo": "bar"}


@pytest.mark.parametrize(*home_and_collect_method_and_endpoints)
@responses.activate
def test_order_capture_passes_without_checkout_and_service_area(
    monkeypatch: pytest.MonkeyPatch,
    order_capture: OrderCapture,
    method: Callable[..., Any],
    endpoint: str,
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
                    "serviceArea": None,
                    "preliminaryAddressInfo": None,
                }
            ),
        ],
    )

    responses.add(
        responses.POST,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/service-area",
        json={"id": "myarea"},
        match=[
            responses.matchers.json_params_matcher(  # type: ignore
                {"zipCode": copy(order_capture._zip_code)}
            )
        ],
    )

    responses.add(
        responses.GET,
        url=f"{order_capture.endpoint}/checkouts/mycheckout/service-area/myarea/{endpoint}",
        json={"foo": "bar"},
    )

    assert method(order_capture) == {"foo": "bar"}


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
