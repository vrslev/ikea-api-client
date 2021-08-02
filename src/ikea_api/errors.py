from typing import Any, Dict, List, Optional


class IkeaApiError(Exception):
    ...


class TokenExpiredError(IkeaApiError):
    ...


class NotAuthenticatedError(IkeaApiError):
    ...


class NoItemsParsedError(IkeaApiError):
    ...


class WrongLanguageCodeError(IkeaApiError):
    def __init__(self, err: Dict[str, Any]):
        ext = err["extensions"]
        msg = None
        if "data" in ext:
            msg = ""
            arr: List[str] = []
            for key in ext["data"]:
                arr.append("{}: {}".format(key, ext["data"][key]))
            msg = ", ".join(arr)
        if msg:
            super().__init__(msg)
        else:
            super().__init__()


class WrongZipCodeError(IkeaApiError):
    ...


class TokenDecodeError(IkeaApiError):
    ...


class GraphqlError(IkeaApiError):
    def __init__(self, err: Dict[str, Any]):
        if "path" in err:
            msg = "{}: {}".format(err["message"], err["path"])
        elif "locations" in err:
            msg = "{}: {}".format(err["message"], err["locations"])
        else:
            msg = err["message"]
        super().__init__(msg)


class GraphqlValidationError(GraphqlError):
    ...


class GraphqlParseError(GraphqlError):
    ...


class WrongItemCodeError(IkeaApiError):
    def __init__(self, err: Optional[Dict[str, Any]] = None):
        msg = None
        if err:
            ext = err["extensions"]
            if "data" in ext:
                if "itemNos" in ext["data"]:
                    msg = ext["data"]["itemNos"]
                else:
                    msg = None
            elif "message" in err:
                msg = err["message"]

        super().__init__(msg)


class InvalidRetailUnitError(IkeaApiError):
    ...


class UnauthorizedError(IkeaApiError):
    """Used when somethings wrong with headers or data"""

    def __init__(self, response: Dict[str, Any]):
        if "moreInformation" in response:
            msg = response["moreInformation"]
        else:
            msg = response
        super().__init__(msg)


class NoDeliveryOptionsAvailableError(IkeaApiError):
    ...


class ServerError(IkeaApiError):
    def __init__(self, response: Dict[str, Any]):
        if "message" in response:
            msg = response["message"]
        else:
            msg = response
        super().__init__(msg)


class ItemFetchError(IkeaApiError):
    ...


CODES_TO_ERRORS = {
    "GRAPHQL_VALIDATION_FAILED": GraphqlValidationError,
    "INVALID_LANGUAGE_CODE": WrongLanguageCodeError,
    "GRAPHQL_PARSE_FAILED": GraphqlParseError,
    "INVALID_ITEM_NUMBER": WrongItemCodeError,
    "ITEM_NUMBER_NOT_FOUND": WrongItemCodeError,
    "INTERNAL_ERROR": ServerError,
}
