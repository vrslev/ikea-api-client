from __future__ import annotations

from typing import Any, Dict, List, cast

from ikea_api.abc import ResponseInfo


class APIError(Exception):
    """Generic API related exception."""

    response: ResponseInfo

    def __init__(self, response: ResponseInfo, msg: Any = None) -> None:
        self.response = response
        if msg is None:
            msg = (response.status_code, response.text)
        super().__init__(msg)


class JSONError(APIError):
    pass


class AuthError(APIError):
    pass


class NotSuccessError(APIError):
    pass


class GraphQLError(APIError):
    errors: list[dict[str, Any]]

    def __init__(self, response: ResponseInfo) -> None:
        if isinstance(response.json, dict):
            self.errors = response.json["errors"]
        else:
            assert isinstance(response.json, list)
            self.errors = []

            for chunk in cast(List[Dict[str, Any]], response.json):
                if "errors" in chunk:
                    self.errors += chunk["errors"]

        super().__init__(response, self.errors)


class ItemFetchError(APIError):
    pass


class WrongItemCodeError(ItemFetchError):
    pass


class ProcessingError(APIError):
    pass


class ParsingError(Exception):
    pass
