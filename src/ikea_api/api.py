from __future__ import annotations

from enum import Enum
from json.decoder import JSONDecodeError
from typing import Any

from requests import Session

from .constants import Constants
from .errors import GraphqlError, IkeaApiError, UnauthorizedError


class Method(Enum):
    POST = "POST"
    GET = "GET"


class API:
    """Generic API class"""

    def __init__(self, token: str | None, endpoint: str):
        self._token, self._endpoint = token, endpoint

        self._session = Session()
        self._session.headers.update(
            {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": Constants.LANGUAGE_CODE,
                "Connection": "keep-alive",
                "User-Agent": Constants.USER_AGENT,
                "Origin": Constants.BASE_URL,
                "Referer": Constants.BASE_URL + "/",
            }
        )
        if token is not None:
            self._session.headers["Authorization"] = "Bearer " + token

    def _error_handler(self, status_code: int, response_json: Any):
        pass

    def _basic_error_handler(
        self, status_code: int, response_json: Any | dict[str, Any]
    ):
        if status_code == 401:  # Token did not passed
            raise UnauthorizedError(response_json)

        if "errors" in response_json:  # GraphQL error
            raise GraphqlError(response_json)

    def _call_api(
        self,
        endpoint: str | None = None,
        method: Method = Method.POST,
        headers: dict[str, str] | None = None,
        data: dict[Any, Any] | list[Any] | None = None,
    ):
        """Wrapper for request's post/get with error handling"""
        if not endpoint:
            endpoint = self._endpoint

        if method == Method.GET:
            response = self._session.get(endpoint, headers=headers, params=data)
        elif method == Method.POST:
            response = self._session.post(endpoint, headers=headers, json=data)

        try:
            response_json: dict[Any, Any] = response.json()
        except JSONDecodeError:
            raise IkeaApiError(response.status_code, response.text)

        self._basic_error_handler(response.status_code, response_json)
        self._error_handler(response.status_code, response_json)

        if not response.ok:
            raise IkeaApiError(response.status_code, response.text)

        return response_json
