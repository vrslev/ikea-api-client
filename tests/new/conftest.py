import json
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest

from new.abc import EndpointInfo, ResponseInfo
from new.constants import Constants


@pytest.fixture(scope="session")
def constants():
    return Constants()


@dataclass
class MockResponseInfo(ResponseInfo[None]):
    headers: dict[str, str] = field(default_factory=dict)
    status_code: int = 200
    text_: str | None = None
    json_: Any = None
    response: None = field(default=None, init=False)

    @cached_property
    def text(self) -> str:
        return self.text_ or self.json_ or ""

    @cached_property
    def json(self) -> Any:
        if self.json_ is None:
            json.loads("")
        return self.json_


class EndpointTester:
    def __init__(self, endpoint: EndpointInfo[Any]) -> None:
        self.endpoint = endpoint
        self.gen = endpoint.func()
        self.next_request = next(self.gen)
        self.response = None

    def prepare(self):
        if not self.next_request:
            raise RuntimeError("All done!")
        req = self.next_request
        self.next_request = None
        return req

    def parse(self, response_info: ResponseInfo[Any], handle_errors: bool = False):
        if handle_errors:
            for handler in self.endpoint.handlers:
                handler(response_info)

        try:
            self.next_request = self.gen.send(response_info)
        except StopIteration as exc:
            return exc.value

    def assert_json_returned(self):
        mock = MagicMock()
        prop = PropertyMock()
        type(mock).json = prop

        self.parse(mock)
        prop.assert_called_once_with()
