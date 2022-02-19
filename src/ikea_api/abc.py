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
    ParamSpec,
    TypeVar,
)

from ikea_api.constants import Constants, get_default_headers


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


LibResponse = TypeVar("LibResponse")


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


EndpointResponse = TypeVar("EndpointResponse")
Endpoint = Generator[RequestInfo, ResponseInfo, EndpointResponse]

ErrorHandler = Callable[[ResponseInfo], None]


@dataclass
class EndpointInfo(Generic[EndpointResponse]):
    func: Callable[[], Endpoint[EndpointResponse]]
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


class BaseAPI(ABC):  # TODO: Move constants to IkeaAPI or something
    const: Constants
    session_info: SessionInfo

    def __init__(self, constants: Constants) -> None:
        self.const = constants
        self.session_info = self.get_session_info()

    def extend_default_headers(self, headers: dict[str, str]) -> dict[str, str]:
        res = get_default_headers(constants=self.const)
        res.update(headers)
        return res

    @abstractmethod
    def get_session_info(self) -> SessionInfo:
        pass

    def RequestInfo(
        self,
        method: Literal["GET", "POST"],
        url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
        data: Any = None,
    ) -> RequestInfo:
        return RequestInfo(
            session_info=self.session_info,
            method=method,
            url=url or "",
            params=params or {},
            headers=headers or {},
            data=data,
            json=json,
        )
