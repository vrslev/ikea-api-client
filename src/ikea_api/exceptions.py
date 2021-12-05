from __future__ import annotations

from typing import TYPE_CHECKING, Any

from requests import Response

if TYPE_CHECKING:
    from ikea_api._api import CustomResponse, GraphQLResponse


class IKEAAPIError(Exception):
    """Generic API related exception."""

    response: CustomResponse

    def __init__(self, response: CustomResponse, msg: Any = None):
        self.response = response
        if msg is None:
            msg = (response.status_code, response.text)
        super().__init__(msg)


class UnauthorizedError(IKEAAPIError):
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


class GraphQLError(IKEAAPIError):
    """Generic GraphQL exception"""

    errors: list[dict[str, Any]] | dict[str, Any]

    def __init__(self, response: CustomResponse):
        resp: GraphQLResponse | list[GraphQLResponse] = response._json

        if isinstance(resp, dict):
            self.errors = resp["errors"]  # type: ignore
        else:
            # from purchases.order_info
            self.errors = [d["errors"] for d in resp if "errors" in d]  # type: ignore

        super().__init__(response, self.errors)


class ItemFetchError(IKEAAPIError):
    response: Response  # type: ignore

    def __init__(self, response: Response, msg: Any = None):
        super().__init__(response, msg=msg)  # type: ignore


class OrderCaptureError(IKEAAPIError):
    error_code: int | None

    def __init__(self, response: CustomResponse):
        self.error_code = response._json.get("errorCode")
        super().__init__(response)


class NoDeliveryOptionsAvailableError(OrderCaptureError):
    pass


class ParsingError(Exception):
    pass
