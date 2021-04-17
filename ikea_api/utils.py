import re
from .errors import NoItemsParsedError


def check_response(response):
    if not response.ok:
        raise Exception(response.status_code, response.content)


def parse_item_code(item_code):
    def parse(item_code):
        found = re.search(
            r'\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}', str(item_code))
        try:
            clean = re.sub(r'[^0-9]+', '', found[0])
        except TypeError:
            clean = None
        return clean

    if isinstance(item_code, list):
        res = []
        for i in item_code:
            parsed = parse(i)
            if parsed:
                res.append(parsed)
        if len(res) == 0:
            raise NoItemsParsedError(item_code)
        return res
    elif isinstance(item_code, str):
        parsed = parse(item_code)
        if not parsed:
            raise NoItemsParsedError(item_code)
        return parsed
