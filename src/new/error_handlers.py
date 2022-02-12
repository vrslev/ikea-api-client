from json import JSONDecodeError
from typing import Any

from new.abc import ResponseInfo
from new.exceptions import IKEAAPIError


def handle_json_decode_error(response: ResponseInfo[Any]):
    try:
        response.json
    except JSONDecodeError:
        raise IKEAAPIError(response)


def handle_401(response: ResponseInfo[Any]):
    if response.status_code == 401:
        raise IKEAAPIError(response)
