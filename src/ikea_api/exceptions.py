from __future__ import annotations

from typing import TYPE_CHECKING, Any

from requests import Response

if TYPE_CHECKING:
    from ikea_api._api import CustomResponse, GraphQLResponse


class IkeaApiError(Exception):
    """Generic API related exception."""

    def __init__(self, response: Response, msg: Any = None):
        self.response = response
        if msg is None:
            msg = (response.status_code, response.text)
        super().__init__(msg)


class UnauthorizedError(IkeaApiError):
    """Exception that is being called when cannot log in"""

    def __init__(self, response: CustomResponse):
        resp_json: dict[str, Any] = response._json
        msg = (
            resp_json.get("moreInformation")
            or resp_json.get("error")
            or resp_json.get("title")  # From Cart
            or resp_json
        )
        super().__init__(response, msg)


class GraphQLError(IkeaApiError):
    """Generic GraphQL exception"""

    def __init__(self, response: CustomResponse):
        resp: GraphQLResponse | list[GraphQLResponse] = response._json

        if isinstance(resp, dict):
            self.errors = resp["errors"]
        else:
            # from purchases.order_info
            self.errors = [d["errors"] for d in resp if "errors" in d]

        super().__init__(response, self.errors)


class ItemFetchError(IkeaApiError):
    pass


class OrderCaptureError(IkeaApiError):
    def __init__(self, response: CustomResponse):
        self.error_code = response._json.get("errorCode")
        super().__init__(response)


class ParsingError(Exception):
    pass
