from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any

import requests

from new.abc import RequestInfo, ResponseInfo, SessionInfo


@dataclass
class RequestsResponseData(ResponseInfo[Any, requests.Response]):
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
def get_cached_session(headers: frozenset[tuple[str, str]]) -> requests.Session:
    session = requests.Session()
    session.headers.update(headers)
    return session


def get_session_from_session_info(session_info: SessionInfo) -> requests.Session:
    return get_cached_session(headers=frozenset(session_info.headers.items()))


def executor(
    session_info: SessionInfo, request_info: RequestInfo
) -> RequestsResponseData:
    session = get_session_from_session_info(session_info)
    response = session.request(
        method=request_info.method,
        url=request_info.url,
        params=request_info.params,
        data=request_info.data,
        json=request_info.json,
        headers=request_info.headers,
    )
    return RequestsResponseData(response)
