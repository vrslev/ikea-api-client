from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, Generator, Generic, Literal, TypeVar, cast

from requests.structures import CaseInsensitiveDict

from new.constants import Constants

PreparedData = TypeVar("PreparedData")
LibResponse = TypeVar("LibResponse")
EndpointResponse = TypeVar("EndpointResponse")


@dataclass
class RequestInfo:
    method: Literal["GET", "POST"]
    url: str
    params: dict[str, Any] | None = None
    data: Any = None
    json: Any = None
    headers: dict[str, str] | None = None


@dataclass
class ResponseInfo(ABC, Generic[LibResponse]):
    response: LibResponse
    headers: CaseInsensitiveDict[str] = field(init=False)
    status_code: int = field(init=False)

    @cached_property
    @abstractmethod
    def text(self) -> str:
        ...

    @cached_property
    @abstractmethod
    def json(self) -> Any:
        ...


@dataclass
class Rerun(Generic[PreparedData]):
    data: PreparedData


@dataclass
class SessionInfo:
    base_url: str
    headers: dict[str, str]


class BaseAPI(ABC):
    const: Constants
    session_info: SessionInfo = field(init=False)

    def __init__(self, constants: Constants):
        self.const = constants
        self.session_info = self.get_session_info()

    @abstractmethod
    def get_session_info(self) -> SessionInfo:
        pass


Endpoint = Generator[
    RequestInfo, ResponseInfo[Any], Rerun[PreparedData] | EndpointResponse
]
EndpointInstMethod = Callable[
    [Any, PreparedData], Endpoint[PreparedData, EndpointResponse]
]
EndpointFunc = Callable[[PreparedData], Endpoint[PreparedData, EndpointResponse]]
ErrorHandler = Callable[[ResponseInfo[Any]], None]
Executor = Callable[[SessionInfo, RequestInfo], ResponseInfo[Any]]


def endpoint(
    func: EndpointInstMethod[PreparedData, EndpointResponse]
) -> EndpointInstMethod[PreparedData, EndpointResponse]:
    return func


def add_handler(handler: ErrorHandler):
    def decorator(
        func: EndpointInstMethod[PreparedData, EndpointResponse]
    ) -> EndpointInstMethod[PreparedData, EndpointResponse]:
        if not getattr(func, "error_handlers", None):
            func.error_handlers: list[ErrorHandler] = []  # type: ignore
        func.error_handlers.append(handler)  # type: ignore
        return func

    return decorator


def get_request_info(gen: Endpoint[Any, Any]) -> RequestInfo:
    return next(gen)


def get_parsed_response(
    gen: Endpoint[Any, EndpointResponse],
    response_info: ResponseInfo[Any],
) -> EndpointResponse:
    try:
        gen.send(response_info)
    except StopIteration as exc:
        return exc.value
    else:
        raise Exception


def before_run(
    func: EndpointFunc[PreparedData, EndpointResponse],
    gen: Endpoint[PreparedData, EndpointResponse],
) -> tuple[SessionInfo, RequestInfo]:
    session_info = cast(SessionInfo, func.__self__.session_info)  # type: ignore

    req_info = get_request_info(gen)
    req_info.url = session_info.base_url + req_info.url

    return session_info, req_info


def after_run(
    func: EndpointFunc[PreparedData, EndpointResponse],
    gen: Endpoint[PreparedData, EndpointResponse],
    response_info: ResponseInfo[Any],
) -> tuple[Rerun[PreparedData], None] | tuple[None, EndpointResponse]:
    for handler in getattr(func, "error_handlers", ()):
        handler(response_info)

    parsed_response = get_parsed_response(gen, response_info)

    if isinstance(parsed_response, Rerun):
        return cast(Rerun[PreparedData], parsed_response), None

    return None, parsed_response
