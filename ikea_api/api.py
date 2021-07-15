from json.decoder import JSONDecodeError
from typing import Any, Dict

from requests import Session

from .constants import Constants
from .errors import (
    CODES_TO_ERRORS,
    NotAuthenticatedError,
    TokenDecodeError,
    TokenExpiredError,
)
from .utils import get_config_values


class API:
    def __init__(self, token: str, endpoint: str):
        self.token, self.endpoint = token, endpoint

        config = get_config_values()
        self.country_code = config["country_code"]
        self.language_code = config["language_code"]

        self.session = Session()
        self.session.headers.update(
            {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": self.language_code,
                "Connection": "keep-alive",
                "User-Agent": Constants.USER_AGENT,
                "Authorization": "Bearer " + token,
                "Origin": Constants.BASE_URL,
                "Referer": Constants.BASE_URL + "/",
            }
        )

    def error_handler(self, status_code, response_json):
        pass

    def basic_error_handler(self, status_code, response_json):
        err = None
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

            ext = err.get("extensions")
            if ext:
                if "errorCode" in ext and ext["errorCode"] == 401:
                    raise NotAuthenticatedError
                elif "code" in ext:
                    if ext["code"] in CODES_TO_ERRORS:
                        raise CODES_TO_ERRORS[ext["code"]](err)
                    else:
                        raise Exception(ext["code"] + ", " + str(err))
            else:
                if "message" in err:
                    raise Exception(err["message"])
                else:
                    raise Exception(err)

    def call_api(self, endpoint=None, headers=None, data=None) -> Dict[str, Any]:
        """Wrapper for request's post/get with error handling"""
        if not endpoint:
            endpoint = self.endpoint

        if data:
            response = self.session.post(endpoint, headers=headers, json=data)
        else:
            response = self.session.get(endpoint, headers=headers)

        try:
            response_json = response.json()
        except JSONDecodeError:
            raise Exception(response.text)

        self.basic_error_handler(response.status_code, response_json)
        self.error_handler(response.status_code, response_json)

        if not response.ok:
            raise Exception(response.status_code, response.text)

        return response_json
