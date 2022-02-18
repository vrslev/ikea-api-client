from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any

import requests

from new.abc import (
    EndpointInfo,
    EndpointResponse,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    SyncExecutor,
)


@dataclass
class RequestsResponseInfo(ResponseInfo[requests.Response]):
    def __post_init__(self) -> None:
        self.headers = self.response.headers
        self.status_code = self.response.status_code

    @cached_property
    def text(self) -> str:
        return self.response.text

    @cached_property
    def json(self) -> Any:
        return self.response.json()


@lru_cache
def get_cached_session(headers: frozenset[tuple[str, str]]) -> requests.Session:
    session = requests.Session()
    session.headers.update(headers)
    return session


def get_session_from_info(session_info: SessionInfo) -> requests.Session:
    return get_cached_session(headers=frozenset(session_info.headers.items()))


class RequestsExecutor(SyncExecutor[requests.Response]):
    @staticmethod
    def request(request: RequestInfo) -> ResponseInfo[requests.Response]:
        session = get_session_from_info(request.session_info)
        response = session.request(
            method=request.method,
            url=request.session_info.base_url + request.url,
            params=request.params,
            data=request.data,
            json=request.json,
            headers=request.headers,
        )
        return RequestsResponseInfo(response)


def run(endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
    return RequestsExecutor.run(endpoint)
