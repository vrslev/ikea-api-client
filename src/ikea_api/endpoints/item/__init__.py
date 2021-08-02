import re
from typing import Any, Callable, Dict, List, Union, overload

from requests import Session

from ikea_api.constants import Constants
from ikea_api.errors import NoItemsParsedError


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


def build_headers(headers: Dict[str, str]):
    new_headers = {
        "Origin": Constants.BASE_URL,
        "User-Agent": Constants.USER_AGENT,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": Constants.LANGUAGE_CODE,
        "Connection": "keep-alive",
    }
    new_headers.update(headers)
    return new_headers


def generic_item_fetcher(  # TODO: Refactor
    items: Union[str, List[str]],
    headers: Dict[str, str],
    func: Callable[..., Any],
    chunk_size: int,
):
    session = Session()
    session.headers.update(build_headers(headers))

    if isinstance(items, str):
        items = [items]
    elif not isinstance(items, list):  # type: ignore
        raise TypeError("String or list required")

    items = [str(i) for i in items]
    items = list(set(items))
    items = parse_item_code(items)

    chunks = [items[x : x + chunk_size] for x in range(0, len(items), chunk_size)]
    responses: List[Any] = []
    for chunk in chunks:
        response = func(session, chunk)
        if isinstance(response, list):
            responses += response
        else:
            responses.append(response)
    return responses
