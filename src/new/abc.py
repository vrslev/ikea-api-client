from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, Generator, Generic, Protocol, TypeVar

from requests.structures import CaseInsensitiveDict

from new.constants import Constants


@dataclass
class RequestInfo:
    method: str
    url: str
    params: dict[str, Any] | None = None
    data: Any = None
    json: Any = None
    headers: dict[str, str] | None = None


PreparedData = TypeVar("PreparedData")
LibResponse = TypeVar("LibResponse")


@dataclass
class ResponseInfo(ABC, Generic[PreparedData, LibResponse]):
    # prep_data: PreparedData
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


EndpointResponse = TypeVar("EndpointResponse")


class Endpoint(ABC, Generic[PreparedData, EndpointResponse]):
    @staticmethod
    @abstractmethod
    def prepare_request(data: PreparedData) -> RequestInfo:
        ...

    @staticmethod
    @abstractmethod
    def get_error_handlers() -> Generator[
        Callable[[ResponseInfo[PreparedData, Any]], None], None, None
    ] | None:
        ...

    @staticmethod
    @abstractmethod
    def parse_response(
        response: ResponseInfo[PreparedData, Any],
    ) -> EndpointResponse | Rerun[PreparedData]:
        ...


@dataclass
class SessionInfo:
    base_url: str
    headers: dict[str, str]


class _GetSessionInfo(Protocol):
    def __call__(self, constants: Constants) -> SessionInfo:
        ...


@dataclass
class RunInfo(Generic[PreparedData, EndpointResponse]):
    session_info_getter: _GetSessionInfo
    endpoint: type[Endpoint[PreparedData, EndpointResponse]]
    data: PreparedData


def prepare_request(
    run_info: RunInfo[Any, Any], constants: Constants
) -> tuple[SessionInfo, RequestInfo]:
    session_info = run_info.session_info_getter(constants)
    req_info = run_info.endpoint.prepare_request(run_info.data)
    req_info.url = session_info.base_url + req_info.url
    return session_info, req_info


def process_response(
    response: LibResponse,
    response_info_cls: type[ResponseInfo[PreparedData, LibResponse]],
    run_info: RunInfo[PreparedData, Any],
):
    resp_info = response_info_cls(run_info.data, response)

    handlers_gen = run_info.endpoint.get_error_handlers()
    if handlers_gen:
        for handler in handlers_gen:
            handler(resp_info)

    return run_info.endpoint.parse_response(resp_info)
