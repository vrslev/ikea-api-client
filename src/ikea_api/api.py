from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Union

from requests import Session

from .constants import Constants
from .errors import (
    CODES_TO_ERRORS,
    IkeaApiError,
    NotAuthenticatedError,
    TokenDecodeError,
    TokenExpiredError,
)

# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
# pyright: reportGeneralTypeIssues=false


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
        self, status_code: int, response_json: Any
    ):  # TODO: Such error handlers are messy
        err: Any = None
        if "error" in response_json and isinstance(err, str) and status_code == 401:
            err = response_json["error"]
            if err == "Token has expired":
                raise TokenExpiredError
            elif err == "Token could not be decoded":
                raise TokenDecodeError
            else:
                raise NotAuthenticatedError(response_json["error"])

        if (
            isinstance(response_json, list)
            and len(response_json) > 0
            and isinstance(response_json[0], dict)
            and response_json[0].get("errors")
        ):
            err = response_json[0]["errors"]

        if isinstance(response_json, dict):
            if "errors" in response_json:
                err = response_json["errors"]

        if err:
            if isinstance(err, list):
                err = err[0]

            ext: Any = err.get("extensions")
            if ext:
                if "errorCode" in ext and ext["errorCode"] == 401:
                    raise NotAuthenticatedError
                elif "code" in ext:
                    if ext["code"] in CODES_TO_ERRORS:
                        raise CODES_TO_ERRORS[ext["code"]](err)
                    else:
                        raise IkeaApiError(ext["code"] + ", " + str(err))
            else:
                if "message" in err:
                    raise IkeaApiError(err["message"])
                else:
                    raise IkeaApiError(err)

    def _call_api(
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
