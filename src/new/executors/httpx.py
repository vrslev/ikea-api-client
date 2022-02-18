from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any, cast

import httpx

from new.abc import (
    AsyncExecutor,
    EndpointInfo,
    EndpointResponse,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
)


@dataclass
class HttpxResponseInfo(ResponseInfo[httpx.Response]):
    def __post_init__(self):
        self.headers = cast(httpx.Headers, self.response.headers)  # type: ignore
        self.status_code = cast(int, self.response.status_code)  # type: ignore

    @cached_property
    def text(self) -> str:
        return cast(str, self.response.text)  # type: ignore

    @cached_property
    def json(self) -> Any:
        return self.response.json()


@lru_cache
def get_cached_session(
    headers: frozenset[tuple[str, str]], base_url: str
) -> httpx.Client:
    return httpx.Client(headers=dict(headers), base_url=base_url)


def get_session_from_info(session_info: SessionInfo) -> httpx.Client:
    return get_cached_session(
        headers=frozenset(session_info.headers.items()), base_url=session_info.base_url
    )


class HttpxExecutor(AsyncExecutor[httpx.Response]):
    @staticmethod
    async def request(
        session_info: SessionInfo, request_info: RequestInfo
    ) -> ResponseInfo[httpx.Response]:
        session = get_session_from_info(session_info)
        response = session.request(  # type: ignore
            method=request_info.method,
            url=request_info.url,
            params=request_info.params,
            data=request_info.data,
            json=request_info.json,
            headers=request_info.headers or {},
        )
        print(response.request)
        return HttpxResponseInfo(response)


async def run(endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
    return await HttpxExecutor.run(endpoint)
