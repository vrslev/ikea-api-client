from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property, partial
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Literal,
    Mapping,
    TypeVar,
)

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


@dataclass
class SessionInfo:
    base_url: str
    headers: dict[str, str]


@dataclass
class RequestInfo:
    session_info: SessionInfo
    method: Literal["GET", "POST"]
    url: str
    params: dict[str, Any]
    headers: dict[str, str]
    data: Any = None
    json: Any = None


@dataclass
class ResponseInfo(ABC):
    headers: Mapping[str, str] = field(init=False)
    status_code: int = field(init=False)

    @cached_property
    @abstractmethod
    def text(self) -> str:
        ...

    @cached_property
    @abstractmethod
    def json(self) -> Any:
        ...

    @property
    @abstractmethod
    def is_success(self) -> bool:
        ...


EndpointResponse = TypeVar("EndpointResponse")
Endpoint = Generator[RequestInfo, ResponseInfo, EndpointResponse]

ErrorHandler = Callable[[ResponseInfo], None]


@dataclass
class EndpointInfo(Generic[EndpointResponse]):
    func: partial[Endpoint[EndpointResponse]]
    handlers: Iterable[ErrorHandler]


P = ParamSpec("P")


def endpoint(
    handlers: Iterable[ErrorHandler] | None = None,
) -> Callable[
    [Callable[P, Endpoint[EndpointResponse]]],
    Callable[P, EndpointInfo[EndpointResponse]],
]:
    def decorator(
        func: Callable[P, Endpoint[EndpointResponse]]
    ) -> Callable[P, EndpointInfo[EndpointResponse]]:
        def wrapper(
            *args: P.args, **kwargs: P.kwargs
        ) -> EndpointInfo[EndpointResponse]:
            return EndpointInfo(
                func=partial(func, *args, **kwargs), handlers=handlers or ()
            )

        return wrapper

    return decorator


class SyncExecutor(ABC):
    @staticmethod
    @abstractmethod
    def request(request: RequestInfo) -> ResponseInfo:
        ...

    @classmethod
    def run(cls, endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
        gen = endpoint.func()
        req_info = next(gen)

        while True:
            response_info = cls.request(req_info)

            try:
                for handler in endpoint.handlers:
                    handler(response_info)
                req_info = gen.send(response_info)

            except StopIteration as exc:
                return exc.value


class AsyncExecutor(ABC):
    @staticmethod
    @abstractmethod
    async def request(request: RequestInfo) -> ResponseInfo:
        ...

    @classmethod
    async def run(cls, endpoint: EndpointInfo[EndpointResponse]) -> EndpointResponse:
        gen = endpoint.func()
        req_info = next(gen)

        while True:
            response_info = await cls.request(req_info)

            try:
                for handler in endpoint.handlers:
                    handler(response_info)
                req_info = gen.send(response_info)

            except StopIteration as exc:
                return exc.value


class BaseAPI(ABC):
    _session_info: SessionInfo

    def __init__(self) -> None:
        self._session_info = self._get_session_info()

    @abstractmethod
    def _get_session_info(self) -> SessionInfo:
        pass

    def _RequestInfo(
        self,
        method: Literal["GET", "POST"],
        url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
        data: Any = None,
    ) -> RequestInfo:
        return RequestInfo(
            session_info=self._session_info,
            method=method,
            url=url or "",
            params=params or {},
            headers=headers or {},
            data=data,
            json=json,
        )
