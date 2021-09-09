from __future__ import annotations

from typing import Any


class IkeaApiError(Exception):
    """Generic API related exception."""


class GraphqlError(IkeaApiError):
    """Generic GraphQL exception"""

    def __init__(self, response: dict[str, Any]):
        self.errors: list[dict[str, Any]] | None = response.get("errors")
        if self.errors:
            msg = "\\\n" + "\n".join(str(e) for e in self.errors)
        else:
            msg = response
        super().__init__(msg)


class UnauthorizedError(IkeaApiError):
    """Exception that is being called when cannot log in"""

    def __init__(self, response: dict[str, Any]):
        msg = response.get("moreInformation") or response.get("error") or response
        super().__init__(msg)


class ItemFetchError(IkeaApiError):
    pass


class OrderCaptureError(IkeaApiError):
    def __init__(self, response: dict[str, Any]):
        self.error_code = response.get("errorCode")
        super().__init__(response)
