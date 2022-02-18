from types import SimpleNamespace

import pytest

from ikea_api.constants import Constants
from ikea_api.wrappers.parsers.purchases import (
    get_history_datetime,
    parse_costs_order,
    parse_history,
    parse_status_banner_order,
)
from tests.conftest import TestData


def test_parse_status_banner_order():
    parse_status_banner_order(TestData.purchases_status_banner)


def test_parse_costs_order():
    parse_costs_order(TestData.purchases_costs)


@pytest.mark.parametrize(
    ("date", "time"), (("val1", "val2"), ("2021-04-14", "18:16:25Z"))
)
def test_get_history_datetime(date: str, time: str):
    assert (
        get_history_datetime(
            SimpleNamespace(dateAndTime=SimpleNamespace(date=date, time=time))  # type: ignore
        )
        == f"{date}T{time}"
    )


def test_parse_history(constants: Constants):
    parse_history(constants, TestData.purchases_history)
