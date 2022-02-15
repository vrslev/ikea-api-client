from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import (
    Any,
    Callable,
    Concatenate,
    Generator,
    Generic,
    Literal,
    ParamSpec,
    TypeVar,
)

from requests.structures import CaseInsensitiveDict

from new.constants import Constants, extend_default_headers

LibResponse = TypeVar("LibResponse")


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


EndpointResponse = TypeVar("EndpointResponse")
Endpoint = Generator[RequestInfo, ResponseInfo[Any], EndpointResponse]

EndpointParams = ParamSpec("EndpointParams")
EndpointMethod = Callable[EndpointParams, Endpoint[EndpointResponse]]
EndpointFunc = Callable[Concatenate[EndpointParams], Endpoint[EndpointResponse]]


@dataclass
class SessionInfo:
    base_url: str
    headers: dict[str, str]


class BaseAPI(ABC):
    const: Constants
    session_info: SessionInfo

    def __init__(self, constants: Constants):
        self.const = constants
        self.session_info = self.get_session_info()

    def extend_default_headers(self, headers: dict[str, str]):
        return extend_default_headers(headers=headers, constants=self.const)

    @abstractmethod
    def get_session_info(self) -> SessionInfo:
        pass


ErrorHandler = Callable[[ResponseInfo[Any]], None]


def add_handler(handler: ErrorHandler):
    def decorator(
        func: EndpointMethod[EndpointParams, EndpointResponse]
    ) -> EndpointMethod[EndpointParams, EndpointResponse]:
        if not getattr(func, "error_handlers", None):
            func.error_handlers: list[ErrorHandler] = []  # type: ignore
        func.error_handlers.append(handler)  # type: ignore
        return func

    return decorator


def get_request_info(gen: Endpoint[Any]) -> RequestInfo:
    return next(gen)


def get_parsed_response(
    gen: Endpoint[EndpointResponse], response_info: ResponseInfo[Any]
) -> EndpointResponse:
    try:
        gen.send(response_info)
    except StopIteration as exc:
        return exc.value
    else:
        raise Exception


def get_instance_from_gen(gen: Endpoint[Any]) -> BaseAPI:
    return gen.gi_frame.f_locals["self"]


def get_func_from_gen(gen: Endpoint[EndpointResponse]) -> Callable[..., Any]:
    return getattr(get_instance_from_gen(gen), gen.gi_code.co_name)


def before_run(gen: Endpoint[Any]) -> tuple[SessionInfo, RequestInfo]:
    session_info = get_instance_from_gen(gen).session_info

    req_info = get_request_info(gen)
    req_info.url = session_info.base_url + req_info.url

    return session_info, req_info


def after_run(
    gen: Endpoint[EndpointResponse], response_info: ResponseInfo[Any]
) -> EndpointResponse:
    func = get_func_from_gen(gen)
    for handler in getattr(func, "error_handlers", ()):
        handler(response_info)

    return get_parsed_response(gen, response_info)
