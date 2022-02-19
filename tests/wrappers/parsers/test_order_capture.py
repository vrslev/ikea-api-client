from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.constants import Constants
from ikea_api.utils import translate_from_dict
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.order_capture import (
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


@pytest.mark.parametrize(
    "v",
    (
        [],
        [SimpleNamespace(timeWindows=None)],
        [
            SimpleNamespace(timeWindows=None),
            SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
        ],
    ),
)
def test_get_date_no_value(v: Any):
    assert get_date(v) is None


def test_get_date_with_value_first():
    exp_datetime = datetime.now()
    deliveries: list[Any] = [
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
    assert get_date(deliveries) == exp_datetime


def test_get_date_with_value_not_first():
    exp_datetime = datetime.now()
    deliveries: list[Any] = [
        SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(fromDateTime=exp_datetime)
            )
        ),
    ]
    assert get_date(deliveries) == exp_datetime


def test_get_type_no_service_type(constants: Constants):
    exp_delivery_type = "HOME_DELIVERY"
    service: Any = SimpleNamespace(
        fulfillmentMethodType=exp_delivery_type, solution=None
    )
    assert get_type(constants, service) == translate_from_dict(
        constants, DELIVERY_TYPES, exp_delivery_type
    )


def test_get_type_with_service_type(constants: Constants):
    exp_delivery_type = "HOME_DELIVERY"
    exp_solution_type = "CURBSIDE"
    service: Any = SimpleNamespace(
        fulfillmentMethodType=exp_delivery_type, solution=exp_solution_type
    )
    exp_res = (
        translate_from_dict(constants, DELIVERY_TYPES, exp_delivery_type)
        + " "
        + translate_from_dict(constants, SERVICE_TYPES, exp_solution_type)
    )
    assert get_type(constants, service) == exp_res


def test_get_price_no_value():
    service: Any = SimpleNamespace(solutionPrice=None)
    assert get_price(service) == 0


def test_get_price_with_value():
    service: Any = SimpleNamespace(solutionPrice=SimpleNamespace(inclTax=100))
    assert get_price(service) == 100


@pytest.mark.parametrize("v", (None, []))
def test_get_unavailable_items_no_value(v: list[Any] | None):
    service: Any = SimpleNamespace(unavailableItems=v)
    assert get_unavailable_items(service) == []


def test_get_unavailable_items_with_value():
    service: Any = SimpleNamespace(
        unavailableItems=[
            SimpleNamespace(itemNo="11111111", availableQuantity=5),
            SimpleNamespace(itemNo="22222222", availableQuantity=3),
        ]
    )
    exp_res = [
        types.UnavailableItem(item_code="11111111", available_qty=5),
        types.UnavailableItem(item_code="22222222", available_qty=3),
    ]
    assert get_unavailable_items(service) == exp_res


def test_get_service_provider_no_value(constants: Constants):
    point: Any = SimpleNamespace(identifier=None)
    assert get_service_provider(constants, point) is None


@pytest.mark.parametrize("v", ("BUSINESSLINES and some other value", "BUSINESSLINES"))
def test_get_service_provider_with_value_match(constants: Constants, v: str):
    point: Any = SimpleNamespace(identifier=v)
    assert get_service_provider(constants, point) == "Деловые линии"


def test_get_service_provider_with_value_no_match(constants: Constants):
    exp_identifier = "USINESSLIN"
    point: Any = SimpleNamespace(identifier=exp_identifier)
    assert get_service_provider(constants, point) == exp_identifier


@pytest.mark.parametrize("response", TestData.order_capture_home)
def test_parse_home_delivery_services(constants: Constants, response: dict[str, Any]):
    parse_home_delivery_services(constants, response)


@pytest.mark.parametrize("response", TestData.order_capture_collect)
def test_parse_collect_delivery_services(
    constants: Constants, response: dict[str, Any]
):
    parse_collect_delivery_services(constants, response)
