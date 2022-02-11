from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any

import requests

from new import abc
from new.constants import Constants


@dataclass
class RequestsResponseData(abc.ResponseInfo[Any, requests.Response]):
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


def get_session_from_session_data(session_data: abc.SessionInfo) -> requests.Session:
    session = get_cached_session(headers=frozenset(session_data.headers.items()))
    return session


def run(
    run_data: abc.RunInfo[Any, abc.EndpointResponse], constants: Constants
) -> abc.EndpointResponse:
    session_data, req_data = abc.prepare_request(run_data, constants)

    session = get_session_from_session_data(session_data)
    response = session.request(
        method=req_data.method,
        url=req_data.url,
        params=req_data.params,
        data=req_data.data,
        json=req_data.json,
        headers=req_data.headers,
    )

    parsed_response = abc.process_response(
        response, response_info_cls=RequestsResponseData, run_info=run_data
    )

    if isinstance(parsed_response, abc.Rerun):
        run_data.data = parsed_response.data
        return run(run_data=run_data, constants=constants)

    return parsed_response
