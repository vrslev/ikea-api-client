from typing import Any, Dict, List


class IkeaApiError(Exception):
    """Generic API related exception."""


class GraphqlError(IkeaApiError):
    """Generic GraphQL exception"""

    def __init__(self, response: Dict[str, Any]):
        errors: List[Dict[str, Any]] = response["errors"]
        pretty_errors: List[str] = ["\\"]
        for e in errors:
            description = None
            if "path" in e:
                description = e["path"]
            elif "locations" in response:
                description = e["locations"]
            msg = f"{e['extensions']['code']} {e['message']}{': ' + description if description else ''}"
            pretty_errors.append(msg)
        super().__init__("\n".join(pretty_errors))


class UnauthorizedError(IkeaApiError):
    """Exception that is being called when cannot log in"""

    def __init__(self, response: Dict[str, Any]):
        msg = response.get("moreInformation") or response.get("error") or response
        super().__init__(msg)


class ItemFetchError(IkeaApiError):
    ...


class OrderCaptureError(IkeaApiError):
    def __init__(self, response: Dict[str, Any]):
        details = (
            ""
            if response["message"] == response["details"]
            else ": " + response["details"]
        )
        msg = f"{response['message']}{details}"
        super().__init__(msg)
