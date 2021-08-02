import re
from typing import Any, List, Union, overload

from requests.models import Response

from .errors import NoItemsParsedError, WrongZipCodeError


def check_response(response: Response) -> None:  # TODO: Move to API
    if not response.ok:
        raise Exception(response.status_code, response.text)


@overload
def parse_item_code(item_code: Union[int, str]) -> str:
    ...


@overload
def parse_item_code(item_code: List[Any]) -> List[str]:
    ...


def parse_item_code(item_code: Union[str, int, List[Any], Any]):  # TODO: Move to item?
    def parse(item_code: Any):
        found = re.search(r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_code))
        res = ""
        if found:
            try:
                res = re.sub(r"[^0-9]+", "", found[0])
            except TypeError:
                pass
        return res

    if isinstance(item_code, list):
        res: List[str] = []
        for i in item_code:
            parsed = parse(i)
            if parsed:
                res.append(parsed)
        if len(res) == 0:
            raise NoItemsParsedError(item_code)
        return res
    elif isinstance(item_code, (str, int)):
        parsed = parse(item_code)
        if not parsed:
            raise NoItemsParsedError(item_code)
        return parsed
    else:
        return ""


def validate_zip_code(zip_code: Union[str, int]):  # MOve to purchases
    if len(re.findall(r"[^0-9]", str(zip_code))) > 0:
        raise WrongZipCodeError(zip_code)
