from types import SimpleNamespace

import pytest

from ikea_api._api import GraphQLResponse
from ikea_api.wrappers._parsers.purchases import (
    get_history_datetime,
    parse_costs_order,
    parse_history,
    parse_status_banner_order,
)
from tests.conftest import get_data_file

status_banner: GraphQLResponse = get_data_file("purchases/status_banner.json")
costs: GraphQLResponse = get_data_file("purchases/costs.json")
history: GraphQLResponse = get_data_file("purchases/history.json")


def test_parse_status_banner_order():
    parse_status_banner_order(status_banner)


def test_parse_costs_order():
    parse_costs_order(costs)


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


def test_parse_history():
    parse_history(history)
