from __future__ import annotations

from json.decoder import JSONDecodeError
from typing import Any

from requests import Session
from typing_extensions import TypedDict

from ikea_api.constants import DEFAULT_HEADERS
from ikea_api.errors import GraphqlError, IkeaApiError, UnauthorizedError


class API:
    """Generic API class"""

    def __init__(self, token: str | None, endpoint: str):
        self.__token, self._endpoint = token, endpoint

        self._session = Session()
        self._session.headers.update(DEFAULT_HEADERS)
        if token is not None:
            self._session.headers["Authorization"] = "Bearer " + token

    @property
    def _token(self):
        if not self.__token:
            raise RuntimeError("No token provided")
        return self.__token

    def _basic_error_handler(self, status_code: int, response: dict[Any, Any]):
        if status_code == 401:  # Token did not passed
            raise UnauthorizedError(response)
        if "errors" in response:
            raise GraphqlError(response)

    def _error_handler(self, status_code: int, response: Any):
        pass

    def _request(
        self,
        endpoint: str | None = None,
        method: str = "POST",
        headers: dict[str, str] | None = None,
        data: dict[Any, Any] | list[Any] | None = None,
    ):
        """Call API and handle errors"""
        if not endpoint:
            endpoint = self._endpoint

        if method == "GET":
            resp = self._session.get(endpoint, headers=headers, params=data)
        elif method == "POST":
            resp = self._session.post(endpoint, headers=headers, json=data)
        else:
            raise RuntimeError(f'Unsupported method: "{method}"')

        try:
            resp_json: Any = resp.json()
        except JSONDecodeError:
            raise IkeaApiError(resp.status_code, resp.text)
        self._basic_error_handler(resp.status_code, resp_json)
        self._error_handler(resp.status_code, resp_json)
        if not resp.ok:
            raise IkeaApiError(resp.status_code, resp.text)
        return resp_json


class GraphQLResponse(TypedDict):
    data: dict[str, Any]
    errors: list[dict[str, Any]] | None
