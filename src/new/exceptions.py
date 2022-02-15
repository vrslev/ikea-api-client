from __future__ import annotations

from typing import Any, cast

from new.abc import ResponseInfo


class APIError(Exception):
    """Generic API related exception."""

    response: ResponseInfo[Any]

    def __init__(self, response: ResponseInfo[Any], msg: Any = None) -> None:
        self.response = response
        if msg is None:
            msg = (response.status_code, response.text)
        super().__init__(msg)


class GraphQLError(APIError):
    errors: list[dict[str, Any]]

    def __init__(self, response: ResponseInfo[Any]) -> None:
        if isinstance(response.json, dict):
            self.errors = response.json["errors"]
        else:
            assert isinstance(response.json, list)
            self.errors = []
            for chunk in cast(list[dict[str, Any]], response.json):
                self.errors.extend(chunk["errors"])

        super().__init__(response, self.errors)


class ItemFetchError(APIError):
    pass


class WrongItemCodeError(ItemFetchError):
    pass
