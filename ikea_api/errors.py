class TokenExpiredError(Exception):
    pass


class NotAuthenticatedError(Exception):
    pass

class WrongItemCodeError(Exception):
    pass

class NoItemsParsedError(Exception):
    pass