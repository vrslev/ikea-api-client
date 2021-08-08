from __future__ import annotations

from typing import Any


class IkeaApiError(Exception):
    """Generic API related exception."""


class GraphqlError(IkeaApiError):
    """Generic GraphQL exception"""

    def __init__(self, response: dict[str, Any]):
        self.errors: list[dict[str, Any]] = response["errors"]
        pretty_errors: list[str] = ["\\"]
        for e in self.errors:
            description = None
            if "path" in e:
                description = e["path"][0]
            elif "locations" in response:
                description = str(e["locations"][0])
            msg = f"{e['extensions']['code']} {e['message']}{': ' + description if description else ''}"
            pretty_errors.append(msg)
        super().__init__("\n".join(pretty_errors))


class UnauthorizedError(IkeaApiError):
    """Exception that is being called when cannot log in"""

    def __init__(self, response: dict[str, Any]):
        msg = response.get("moreInformation") or response.get("error") or response
        super().__init__(msg)


class ItemFetchError(IkeaApiError):
    ...


class OrderCaptureError(IkeaApiError):
    def __init__(self, response: dict[str, Any]):
        self.error_code = response["errorCode"]
        details = (
            ""
            if response["message"] == response["details"]
            else ": " + response["details"]
        )
        msg = f"{response['message']}{details}"
        super().__init__(msg)
