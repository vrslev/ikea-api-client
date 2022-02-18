from json import JSONDecodeError
from typing import Any

from ikea_api.abc import ResponseInfo
from ikea_api.exceptions import APIError, GraphQLError


def handle_json_decode_error(response: ResponseInfo[Any]):
    try:
        response.json
    except JSONDecodeError:
        raise APIError(response)


def handle_401(response: ResponseInfo[Any]):
    if response.status_code == 401:
        raise APIError(response)


def handle_graphql_error(response: ResponseInfo[Any]):
    if "errors" in response.json:
        raise GraphQLError(response)
