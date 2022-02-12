from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, Generator, Generic, TypeVar, cast

from requests.structures import CaseInsensitiveDict

from new.constants import Constants

PreparedData = TypeVar("PreparedData")
LibResponse = TypeVar("LibResponse")
EndpointResponse = TypeVar("EndpointResponse")


@dataclass
class RequestInfo:
    method: str
    url: str
    params: dict[str, Any] | None = None
    data: Any = None
    json: Any = None
    headers: dict[str, str] | None = None


@dataclass
class ResponseInfo(ABC, Generic[PreparedData, LibResponse]):
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
    constants: Constants
    session_info: SessionInfo = field(init=False)

    def __init__(self, constants: Constants):
        self.constants = constants
        self.session_info = self.get_session_info()

    @abstractmethod
    def get_session_info(self) -> SessionInfo:
        pass


Endpoint = Generator[
    RequestInfo, ResponseInfo[PreparedData, Any], Rerun[PreparedData] | EndpointResponse
]
EndpointInstMethod = Callable[
    [Any, PreparedData], Endpoint[PreparedData, EndpointResponse]
]
EndpointFunc = Callable[[PreparedData], Endpoint[PreparedData, EndpointResponse]]
ErrorHandler = Callable[[ResponseInfo[Any, Any]], None]
Executor = Callable[[SessionInfo, RequestInfo], ResponseInfo[PreparedData, Any]]


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


def run(
    executor: Executor[PreparedData],
    func: EndpointFunc[PreparedData, EndpointResponse],
    data: PreparedData,
) -> EndpointResponse:
    generator = func(data)

    session_info = func.__self__.session_info  # type: ignore

    req_info = next(generator)
    req_info.url = session_info.base_url + req_info.url

    response_info = executor(session_info, req_info)

    for handler in getattr(func, "error_handlers", ()):
        handler(response_info)

    try:
        generator.send(response_info)
    except StopIteration as exc:
        parsed_response = exc.value
    else:
        raise Exception

    if isinstance(parsed_response, Rerun):
        new_data = cast(Rerun[PreparedData], parsed_response).data
        return run(executor=executor, func=func, data=new_data)

    return parsed_response
