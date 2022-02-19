from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any, cast

import httpx  # TODO: Optional import

from ikea_api.abc import (
    AsyncExecutor,
    EndpointInfo,
    EndpointResponse,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
)

# TODO: Add Sync client


@dataclass
class HttpxResponseInfo(ResponseInfo):
    response: httpx.Response

    def __post_init__(self) -> None:
        self.headers = cast(httpx.Headers, self.response.headers)  # type: ignore
        self.status_code = cast(int, self.response.status_code)  # type: ignore

    @cached_property
    def text(self) -> str:
        return self.response.text

    @cached_property
    def json(self) -> Any:
        return self.response.json()


@lru_cache
def get_cached_session(headers: frozenset[tuple[str, str]]) -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=dict(headers))


def get_session_from_info(session_info: SessionInfo) -> httpx.AsyncClient:
    return get_cached_session(headers=frozenset(session_info.headers.items()))


class HttpxExecutor(AsyncExecutor):
    @staticmethod
    async def request(request: RequestInfo) -> HttpxResponseInfo:
        session = get_session_from_info(request.session_info)
        response = await session.request(  # type: ignore
            method=request.method,
            url=request.session_info.base_url + request.url,
            params=request.params,
            data=request.data,
            json=request.json,
            headers=request.headers,
        )
        return HttpxResponseInfo(response)


async def run(endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
    return await HttpxExecutor.run(endpoint)
