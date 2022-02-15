from dataclasses import dataclass, field
from functools import cached_property
from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest

from new.abc import Endpoint, ResponseInfo, get_parsed_response, get_request_info
from new.constants import Constants


@pytest.fixture
def constants():
    return Constants()


@dataclass
class MockResponseInfo(ResponseInfo[None]):
    headers: dict[str, str] = field(default_factory=dict)
    status_code: int = 200
    text_: str | None = None
    json_: Any | None = None
    response: None = field(init=False)

    @cached_property
    def text(self) -> str:
        assert self.text_
        return self.text_

    @cached_property
    def json(self) -> Any:
        assert self.json_
        return self.json_


class EndpointTester:
    def __init__(self, gen: Endpoint[Any]) -> None:
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
