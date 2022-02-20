from __future__ import annotations

import json
from typing import Any, Dict, List, cast

from ikea_api.abc import ResponseInfo
from ikea_api.exceptions import AuthError, GraphQLError, JSONError, NotSuccessError


def handle_json_decode_error(response: ResponseInfo) -> None:
    try:
        response.json
    except json.JSONDecodeError:
        raise JSONError(response)


def handle_401(response: ResponseInfo) -> None:
    if response.status_code == 401:
        raise AuthError(response)


def handle_not_success(response: ResponseInfo) -> None:
    if not response.is_success:
        raise NotSuccessError(response)


def handle_graphql_error(response: ResponseInfo) -> None:
    if "errors" in response.json:
        raise GraphQLError(response)
    elif isinstance(response.json, list):
        for dict_ in cast(List[Dict[str, Any]], response.json):
            if "errors" in dict_:
                raise GraphQLError(response)
