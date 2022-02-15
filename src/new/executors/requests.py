from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import TYPE_CHECKING, Any

from new.abc import (
    Endpoint,
    EndpointResponse,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    after_run,
    before_run,
)

if TYPE_CHECKING:
    import requests


@dataclass
class RequestsResponseInfo(ResponseInfo["requests.Response"]):
    def __post_init__(self):
        self.headers = self.response.headers
        self.status_code = self.response.status_code

    @cached_property
    def text(self) -> str:
        return self.response.text

    @cached_property
    def json(self) -> Any:
        return self.response.json()


@lru_cache
def get_cached_session(headers: frozenset[tuple[str, str]]) -> "requests.Session":
    import requests

    session = requests.Session()
    session.headers.update(headers)
    return session


def get_session_from_info(session_info: SessionInfo) -> "requests.Session":
    return get_cached_session(headers=frozenset(session_info.headers.items()))


def run_request(
    session_info: SessionInfo, request_info: RequestInfo
) -> RequestsResponseInfo:
    session = get_session_from_info(session_info)
    response = session.request(
        method=request_info.method,
        url=session_info.base_url + request_info.url,
        params=request_info.params,
        data=request_info.data,
        json=request_info.json,
        headers=request_info.headers,
    )
    return RequestsResponseInfo(response)


def execute(gen: Endpoint[EndpointResponse]) -> EndpointResponse:
    session_info, req_info = before_run(gen)

    while True:
        try:
            response_info = run_request(session_info, req_info)
            req_info = after_run(gen, response_info)
        except StopIteration as exc:
            return exc.value
