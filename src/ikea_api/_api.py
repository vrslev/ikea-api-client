from __future__ import annotations

import sys
from json.decoder import JSONDecodeError
from typing import Any

import requests

from ikea_api._constants import DEFAULT_HEADERS
from ikea_api.exceptions import GraphQLError, IKEAAPIError, UnauthorizedError

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class CustomResponse(requests.Response):
    _json: Any


class API:
    """Generic API class"""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)

    def _basic_error_handler(self, response: CustomResponse):
        if response.status_code == 401:  # Token did not passed
            raise UnauthorizedError(response)

    def _error_handler(self, response: CustomResponse):  # pragma: no cover
        pass

    def _handle_response(self, response: CustomResponse):
        try:
            resp_json = response.json()
        except JSONDecodeError:
            raise IKEAAPIError(response)
        response._json = resp_json
        self._basic_error_handler(response)
        self._error_handler(response)
        if not response.ok:
            raise IKEAAPIError(response)
        return response._json

    def _get(
        self,
        endpoint: str | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        if not endpoint:
            endpoint = self.endpoint
        response: CustomResponse = self._session.get(  # type: ignore
            url=endpoint, headers=headers, params=params
        )
        return self._handle_response(response)

    def _post(
        self,
        endpoint: str | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
    ) -> Any:
        if not endpoint:
            endpoint = self.endpoint
        response: CustomResponse = self._session.post(  # type: ignore
            url=endpoint, headers=headers, json=json
        )
        return self._handle_response(response)


class AuthorizedAPI(API):
    def __init__(self, endpoint: str, token: str | None):
        super().__init__(endpoint)
        self._token = token
        if token is not None:
            self._session.headers["Authorization"] = "Bearer " + token

    @property
    def token(self):
        if not self._token:
            raise RuntimeError("No token provided")
        return self._token


class GraphQLResponse(TypedDict):
    data: dict[str, Any]
    errors: list[dict[str, Any]] | None


class GraphQLAPI(AuthorizedAPI):
    def _basic_error_handler(self, response: CustomResponse):
        super()._basic_error_handler(response)
        if "errors" in response._json:
            raise GraphQLError(response)

    def _post(
        self,
        endpoint: str | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
    ) -> GraphQLResponse:  # pragma: no cover
        return super()._post(endpoint=endpoint, headers=headers, json=json)
