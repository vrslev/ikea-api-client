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


class EndpointTester:
    def __init__(self, gen: Endpoint[EndpointResponse]) -> None:
        self.gen = gen

    def prepare(self):
        return get_request_info(self.gen)

    def parse(self, response_info: ResponseInfo[Any]):
        return get_parsed_response(self.gen, response_info)

    def assert_json_returned(self):
        mock = MagicMock()
        prop = PropertyMock()
        type(mock).json = prop

        self.parse(mock)
        prop.assert_called_once_with()


def test_get_items(ingka_items_api: ingka_items.API):
    item_codes = ["11111111", "22222222"]
    c = EndpointTester(ingka_items_api.get_items(item_codes))

    request_info = c.prepare()
    assert request_info.method == "GET"
    assert request_info.params == {"itemNos": item_codes}

    c.assert_json_returned()
