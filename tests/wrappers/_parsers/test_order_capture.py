from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.wrappers import types
from ikea_api.wrappers._parsers import translate_from_dict
from ikea_api.wrappers._parsers.order_capture import (
    DELIVERY_TYPES,
    SERVICE_TYPES,
    get_date,
    get_price,
    get_service_provider,
    get_type,
    get_unavailable_items,
    parse_collect_delivery_services,
    parse_home_delivery_services,
)
from tests.conftest import TestData


def test_get_date_no_value():
    assert get_date([]) is None
    assert get_date([SimpleNamespace(timeWindows=None)]) is None  # type: ignore
    assert (
        get_date(
            [  # type: ignore
                SimpleNamespace(timeWindows=None),
                SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
            ]
        )
    ) is None


def test_get_date_with_value_first():
    exp_datetime = datetime.now()
    deliveries = [
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(fromDateTime=exp_datetime)
            )
        ),
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(
                    fromDateTime=exp_datetime + timedelta(days=1)
                )
            )
        ),
    ]
    assert get_date(deliveries) == exp_datetime  # type: ignore


def test_get_date_with_value_not_first():
    exp_datetime = datetime.now()
    deliveries = [
        SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(fromDateTime=exp_datetime)
            )
        ),
    ]
    assert get_date(deliveries) == exp_datetime  # type: ignore


def test_get_type_no_service_type():
    exp_delivery_type = "HOME_DELIVERY"
    service = SimpleNamespace(fulfillmentMethodType=exp_delivery_type, solution=None)
    assert get_type(service) == translate_from_dict(DELIVERY_TYPES, exp_delivery_type)  # type: ignore


def test_get_type_with_service_type():
    exp_delivery_type = "HOME_DELIVERY"
    exp_solution_type = "CURBSIDE"
    service = SimpleNamespace(
        fulfillmentMethodType=exp_delivery_type, solution=exp_solution_type
    )
    assert get_type(service) == (  # type: ignore
        translate_from_dict(DELIVERY_TYPES, exp_delivery_type)
        + f" {translate_from_dict(SERVICE_TYPES, exp_solution_type)}"
    )


def test_get_price_no_value():
    service = SimpleNamespace(solutionPrice=None)
    assert get_price(service) == 0  # type: ignore


def test_get_price_with_value():
    service = SimpleNamespace(solutionPrice=SimpleNamespace(inclTax=100))
    assert get_price(service) == 100  # type: ignore


@pytest.mark.parametrize("v", (None, []))
def test_get_unavailable_items_no_value(v: list[Any] | None):
    assert get_unavailable_items(SimpleNamespace(unavailableItems=v)) == []  # type: ignore


def test_get_unavailable_items_with_value():
    items = [
        SimpleNamespace(itemNo="11111111", availableQuantity=5),
        SimpleNamespace(itemNo="22222222", availableQuantity=3),
    ]
    exp_res = [
        types.UnavailableItem(item_code="11111111", available_qty=5),
        types.UnavailableItem(item_code="22222222", available_qty=3),
    ]
    assert get_unavailable_items(SimpleNamespace(unavailableItems=items)) == exp_res  # type: ignore


def test_get_service_provider_no_value():
    assert get_service_provider(SimpleNamespace(identifier=None)) is None  # type: ignore


@pytest.mark.parametrize("v", ("BUSINESSLINES and some other value", "BUSINESSLINES"))
def test_get_service_provider_with_value_match(v: str):
    service = SimpleNamespace(identifier=v)
    assert get_service_provider(service) == "Деловые линии"  # type: ignore


def test_get_service_provider_with_value_no_match():
    exp_identifier = "USINESSLIN"
    service = SimpleNamespace(identifier=exp_identifier)
    assert get_service_provider(service) == exp_identifier  # type: ignore


@pytest.mark.parametrize("response", TestData.order_capture_home)
def test_parse_home_delivery_services(response: dict[str, Any]):
    parse_home_delivery_services(response)


@pytest.mark.parametrize("response", TestData.order_capture_collect)
def test_parse_collect_delivery_services(response: dict[str, Any]):
    parse_collect_delivery_services(response)
