from __future__ import annotations

from json import JSONDecodeError
from typing import Any, Dict, List, cast

from ikea_api.abc import ResponseInfo
from ikea_api.exceptions import AuthError, GraphQLError, JSONError, NotSuccessError


def handle_json_decode_error(response: ResponseInfo):
    try:
        response.json
    except JSONDecodeError:
        raise JSONError(response)


def handle_401(response: ResponseInfo):
    if response.status_code == 401:
        raise AuthError(response)


def handle_not_success(response: ResponseInfo):
    if not response.is_success:
        raise NotSuccessError(response)


def handle_graphql_error(response: ResponseInfo):
    if "errors" in response.json:
        raise GraphQLError(response)
    elif isinstance(response.json, list):
        for dict_ in cast(List[Dict[str, Any]], response.json):
            if "errors" in dict_:
                raise GraphQLError(response)
