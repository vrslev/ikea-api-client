import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from types import FrameType
from typing import (
    Any,
    Callable,
    Concatenate,
    Generator,
    Generic,
    Literal,
    Mapping,
    ParamSpec,
    TypeVar,
)

from new.constants import Constants, extend_default_headers

LibResponse = TypeVar("LibResponse")


@dataclass
class SessionInfo:
    base_url: str
    headers: dict[str, str]


@dataclass
class RequestInfo:
    session_info: SessionInfo
    method: Literal["GET", "POST"]
    url: str
    params: dict[str, Any] | None = None
    data: Any = None
    json: Any = None
    headers: dict[str, str] | None = None


@dataclass
class ResponseInfo(ABC, Generic[LibResponse]):
    response: LibResponse
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
Endpoint = Generator[RequestInfo, ResponseInfo[Any], EndpointResponse]

EndpointParams = ParamSpec("EndpointParams")
EndpointMethod = Callable[EndpointParams, Endpoint[EndpointResponse]]
EndpointFunc = Callable[Concatenate[EndpointParams], Endpoint[EndpointResponse]]


class BaseAPI(ABC):  # TODO: Move constants to IkeaAPI or something
    const: Constants
    session_info: SessionInfo

    def __init__(self, constants: Constants) -> None:
        self.const = constants
        self.session_info = self.get_session_info()

    def extend_default_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return extend_default_headers(headers=headers, constants=self.const)

    @abstractmethod
    def get_session_info(self) -> SessionInfo:
        pass

    def RequestInfo(
        self,
        method: Literal["GET", "POST"],
        url: str,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> RequestInfo:
        return RequestInfo(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            session_info=self.session_info,
        )


ErrorHandler = Callable[[ResponseInfo[Any]], None]
T = TypeVar("T")


def add_handler(handler: ErrorHandler):
    def decorator(func: T) -> T:
        if not getattr(func, "error_handlers", None):
            func.error_handlers: list[ErrorHandler] = []  # type: ignore
        func.error_handlers.append(handler)  # type: ignore
        return func

    return decorator


def get_request_info(gen: Endpoint[Any]) -> RequestInfo:
    return next(gen)


def get_source_gen(gen: Endpoint[Any]) -> Generator[Any, Any, Any]:
    self = gen.gi_frame.f_locals.get("self")
    if self:
        return gen
    if (
        gen.gi_yieldfrom
        and gen.gi_yieldfrom.gi_frame
        and gen.gi_yieldfrom.gi_frame.f_locals.get("self")
    ):
        return gen.gi_yieldfrom
    raise RuntimeError("Frame not found")


# def get_instance_from_gen(gen: Endpoint[Any]) -> BaseAPI:
#     self = gen.gi_frame.f_locals.get("self")
#     if not self and gen.gi_yieldfrom:
#         return gen.gi_yieldfrom.gi_frame.f_locals["self"]
#     assert self
#     return self


def get_self_from_gen(gen: Endpoint[Any]) -> BaseAPI:
    return gen.gi_frame.f_locals["self"]


def get_func_from_gen(gen: Endpoint[EndpointResponse]) -> Callable[..., Any]:
    source_gen = get_source_gen(gen)
    return getattr(get_self_from_gen(source_gen), source_gen.gi_code.co_name)


class SyncExecutor(ABC, Generic[LibResponse]):
    @classmethod
    def after_run(
        cls, gen: Endpoint[EndpointResponse], response_info: ResponseInfo[Any]
    ) -> RequestInfo:
        print("after")
        func = get_func_from_gen(gen)
        try:
            for handler in getattr(func, "error_handlers", ()):
                handler(response_info)
        except Exception as exc:
            gen.throw(exc)

        return gen.send(response_info)

    @staticmethod
    @abstractmethod
    def request(
        session_info: SessionInfo, request_info: RequestInfo
    ) -> ResponseInfo[LibResponse]:
        ...

    @classmethod
    def run(cls, gen: Endpoint[EndpointResponse]) -> EndpointResponse:
        req_info = next(gen)
        func = get_func_from_gen(gen)

        while True:
            try:

                response_info = cls.request(req_info.session_info, req_info)
                try:
                    for handler in getattr(func, "error_handlers", ()):
                        handler(response_info)
                except Exception as exc:
                    pass
                    gen.throw(exc)
                    # get_source_gen(gen).throw(exc)

                req_info = gen.send(response_info)

                try:
                    func = get_func_from_gen(gen)
                except AttributeError:
                    req_info = next(get_source_gen(gen))

            except StopIteration as exc:
                if not gen.gi_yieldfrom or not gen.gi_yieldfrom.gi_frame:
                    print("! NO FRAME DETECTED")
                    continue
                    # return exc.value

                else:
                    # continue
                    return exc.value
