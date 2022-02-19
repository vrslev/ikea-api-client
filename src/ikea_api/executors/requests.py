from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import TYPE_CHECKING, Any

from ikea_api.abc import (
    EndpointInfo,
    EndpointResponse,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    SyncExecutor,
)

if TYPE_CHECKING:
    import requests


@dataclass
class RequestsResponseInfo(ResponseInfo):
    response: requests.Response

    def __post_init__(self) -> None:
        self.headers = self.response.headers
        self.status_code = self.response.status_code

    @cached_property
    def text(self) -> str:
        return self.response.text

    @cached_property
    def json(self) -> Any:
        return self.response.json()

    @property
    def is_success(self) -> bool:
        return self.response.ok


@lru_cache
def get_cached_session(headers: frozenset[tuple[str, str]]) -> requests.Session:
    try:
        import requests
    except ImportError:
        raise RuntimeError(
            "To use requests executor you need requests to be installed. "
            + "Run 'pip install \"ikea_api[requests]\"' to do so."
        )

    session = requests.Session()
    session.headers.update(headers)
    return session


def get_session_from_info(session_info: SessionInfo) -> requests.Session:
    return get_cached_session(headers=frozenset(session_info.headers.items()))


class RequestsExecutor(SyncExecutor):
    @staticmethod
    def request(request: RequestInfo) -> RequestsResponseInfo:
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
