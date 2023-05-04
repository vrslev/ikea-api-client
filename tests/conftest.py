from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Callable
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest

from ikea_api.abc import (
    Endpoint,
    EndpointInfo,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    endpoint,
)
from ikea_api.constants import Constants


def get_data_path(name: str) -> Path:
    return Path(__file__).parent / "data" / name


def get_data_files_in_directory(dirname: str) -> list[Any]:
    def load(path: Path) -> Any:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    files = sorted(list(get_data_path(dirname).glob("*")))
    return [load(path) for path in files]


def get_data_file(filename: str) -> Any:
    with open(get_data_path(filename), encoding="utf-8") as f:
        return json.load(f)


class TestData:
    item_ingka = get_data_files_in_directory("item_ingka")
    item_iows = get_data_files_in_directory("item_iows")
    item_pip = get_data_files_in_directory("item_pip")
    order_capture_home = get_data_files_in_directory("order_capture/home")
    order_capture_collect = get_data_files_in_directory("order_capture/collect")
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

    @property
    def is_success(self) -> bool:
        return True


class EndpointTester:
    def __init__(self, endpoint: EndpointInfo[Any]) -> None:
        self.endpoint = endpoint
        self.gen = endpoint.func()
        self.next_request = next(self.gen)
        self.response = None

    def prepare(self):
        if not self.next_request:
            raise NotImplementedError("All done!")
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
        prop.assert_called()


@dataclass
class ExecutorContext:
    request: RequestInfo
    response: ResponseInfo
    func: Callable[[], EndpointInfo[Any]]
    endpoint_response: Any
    handler: Mock


@pytest.fixture
def executor_context():
    request = RequestInfo(
        SessionInfo(
            base_url="https://example.com",
            headers={"Accept": "*/*"},
        ),
        method="POST",
        url="/ping",
        params={"foo": "bar"},
        headers={"Referer": "https://example.com"},
        data='{"ok":"ok"}',
        json={"ok": "ok"},
    )
    response = MockResponseInfo(
        headers={"X-ok": "ok"}, status_code=200, text_='{"ok":"ok"}', json_={"ok": "ok"}
    )
    handler = MagicMock()

    @endpoint(handlers=[handler])
    def myendpoint() -> Endpoint[tuple[str, str]]:
        response1 = yield request
        response2 = yield request
        return (response1.json, response2.json)

    yield ExecutorContext(
        request=request,
        response=response,
        func=myendpoint,
        endpoint_response=(response.json, response.json),
        handler=handler,
    )
