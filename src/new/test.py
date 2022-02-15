from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest

from new.abc import (
    Endpoint,
    EndpointResponse,
    ResponseInfo,
    get_parsed_response,
    get_request_info,
)
from new.constants import Constants
from new.endpoints import ingka_items


@pytest.fixture
def constants():
    return Constants()


@pytest.fixture
def ingka_items_api(constants: Constants):
    return ingka_items.API(constants)


class EndpointChecker:
    def __init__(self, gen: Endpoint[EndpointResponse]) -> None:
        self.gen = gen

    def request_info(self):
        return get_request_info(self.gen)

    def parsed_response(self, response_info: ResponseInfo[Any]):
        return get_parsed_response(self.gen, response_info)

    def assert_json_returned(self):
        mock = MagicMock()
        prop = PropertyMock()
        type(mock).json = prop

        self.parsed_response(mock)
        prop.assert_called_once_with()


def test_get_items_prepare(ingka_items_api: ingka_items.API):
    item_codes = ["11111111", "22222222"]
    gen = ingka_items_api.get_items(item_codes)
    checker = EndpointChecker(gen)

    request_info = checker.request_info()
    assert request_info.method == "GET"
    assert request_info.params == {"itemNos": item_codes}

    checker.assert_json_returned()
