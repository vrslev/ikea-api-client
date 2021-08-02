class TokenExpiredError(Exception):
    pass


class NotAuthenticatedError(Exception):
    pass


class NoItemsParsedError(Exception):
    pass


class WrongLanguageCodeError(Exception):
    def __init__(self, err):
        ext = err["extensions"]
        msg = None
        if "data" in ext:
            msg = ""
            arr = []
            for key in ext["data"]:
                arr.append("{}: {}".format(key, ext["data"][key]))
            msg = ", ".join(arr)
        if msg:
            super().__init__(msg)
        else:
            super().__init__()


class WrongZipCodeError(Exception):
    pass


class TokenDecodeError(Exception):
    pass


class GraphqlError(Exception):
    def __init__(self, err):
        if "path" in err:
            msg = "{}: {}".format(err["message"], err["path"])
        elif "locations" in err:
            msg = "{}: {}".format(err["message"], err["locations"])
        else:
            msg = err["message"]
        super().__init__(msg)


class GraphqlValidationError(GraphqlError):
    pass


class GraphqlParseError(GraphqlError):
    pass


class WrongItemCodeError(Exception):
    def __init__(self, err):
        ext = err["extensions"]
        if "data" in ext:
            if "itemNos" in ext["data"]:
                msg = ext["data"]["itemNos"]
            else:
                msg = None
        elif "message" in err:
            msg = err["message"]
        else:
            msg = None

        super().__init__(msg)


class InvalidRetailUnitError(Exception):
    pass


class UnauthorizedError(Exception):
    """Used when somethings wrong with headers or data"""

    def __init__(self, response):
        if "moreInformation" in response:
            msg = response["moreInformation"]
        else:
            msg = response
        super().__init__(msg)


class NoDeliveryOptionsAvailableError(Exception):
    pass


class ServerError(Exception):
    def __init__(self, response):
        if "message" in response:
            msg = response["message"]
        else:
            msg = response
        super().__init__(msg)


CODES_TO_ERRORS = {
    "GRAPHQL_VALIDATION_FAILED": GraphqlValidationError,
    "INVALID_LANGUAGE_CODE": WrongLanguageCodeError,
    "GRAPHQL_PARSE_FAILED": GraphqlParseError,
    "INVALID_ITEM_NUMBER": WrongItemCodeError,
    "ITEM_NUMBER_NOT_FOUND": WrongItemCodeError,
    "INTERNAL_ERROR": ServerError,
}
