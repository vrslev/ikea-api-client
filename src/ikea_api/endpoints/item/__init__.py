from typing import Any, Callable, Dict, List, Union

from requests import Session

from ikea_api.constants import Constants
from ikea_api.utils import parse_item_code


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


def generic_item_fetcher(
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
