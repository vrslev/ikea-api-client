import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest

from ikea_api.abc import EndpointInfo, ResponseInfo
from ikea_api.constants import Constants


def get_files_in_directory(dirname: str):
    return (Path(__file__).parent / "data" / dirname).glob("*")


def get_all_data_files_in_directory(dirname: str):
    res: list[Any] = []
    for path in get_files_in_directory(dirname):
        with open(path) as f:
            res.append(json.load(f))
    return res


def get_data_file(filename: str):
    path = Path(__file__).parent / "data" / filename
    with open(path) as f:
        return json.load(f)


class TestData:
    item_ingka = get_all_data_files_in_directory("item_ingka")
    item_iows = get_all_data_files_in_directory("item_iows")
    item_pip = get_all_data_files_in_directory("item_pip")
    order_capture_home = get_all_data_files_in_directory("order_capture/home")
    order_capture_collect = get_all_data_files_in_directory("order_capture/collect")
    purchases_status_banner = get_data_file("purchases/status_banner.json")
    purchases_costs = get_data_file("purchases/costs.json")
    purchases_history = get_data_file("purchases/history.json")


@pytest.fixture(scope="session")
def constants():
    return Constants()


@dataclass
class MockResponseInfo(ResponseInfo):
    headers: dict[str, str] = field(default_factory=dict)
    status_code: int = 200
    text_: str | None = None
    json_: Any = None

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

    def parse(self, response_info: ResponseInfo, handle_errors: bool = False):
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
