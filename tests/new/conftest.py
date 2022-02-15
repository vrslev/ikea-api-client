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


@pytest.fixture
def constants():
    return Constants()


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
