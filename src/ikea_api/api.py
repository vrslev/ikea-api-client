from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Union

from requests import Session

from .constants import Constants
from .errors import GraphqlError, IkeaApiError, UnauthorizedError

## pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
## pyright: reportGeneralTypeIssues=false


class API:
    def __init__(self, token: str, endpoint: str):
        self._token, self._endpoint = token, endpoint

        self._country_code = Constants.COUNTRY_CODE
        self._language_code = Constants.LANGUAGE_CODE

        self._session = Session()
        self._session.headers.update(
            {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": self._language_code,
                "Connection": "keep-alive",
                "User-Agent": Constants.USER_AGENT,
                "Authorization": "Bearer " + token,
                "Origin": Constants.BASE_URL,
                "Referer": Constants.BASE_URL + "/",
            }
        )

    def _error_handler(self, status_code: int, response_json: Any):
        pass

    def _basic_error_handler(
        self, status_code: int, response_json: Union[Any, Dict[str, Any]]
    ):
        if status_code == 401:  # Token did not passed
            raise UnauthorizedError(response_json)

        if "errors" in response_json:  # GraphQL error
            raise GraphqlError(response_json)

    def _call_api(  # TODO: Add choice between GET and POST
        self,
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[Any, Any], List[Any]]] = None,
    ):
        """Wrapper for request's post/get with error handling"""
        if not endpoint:
            endpoint = self._endpoint

        if data:
            response = self._session.post(endpoint, headers=headers, json=data)
        else:
            response = self._session.get(endpoint, headers=headers)

        try:
            response_json: Dict[Any, Any] = response.json()
        except JSONDecodeError:
            raise IkeaApiError(response.text)

        self._basic_error_handler(response.status_code, response_json)
        self._error_handler(response.status_code, response_json)

        if not response.ok:
            raise IkeaApiError(response.status_code, response.text)

        return response_json
