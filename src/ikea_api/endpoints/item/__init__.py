from __future__ import annotations

import re
from typing import Any, Callable, overload

from requests import Session

from ikea_api.constants import Constants

# TODO: Refactor all item endpoints


@overload
def parse_item_code(item_code: int | str) -> str:
    ...


@overload
def parse_item_code(item_code: list[Any]) -> list[str]:
    ...


def parse_item_code(item_code: str | int | list[Any] | Any):
    def parse(item_code: Any):
        found = re.search(r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_code))
        res = ""
        if found:
            try:
                res = re.sub(r"[^0-9]+", "", found[0])
            except TypeError:
                pass
        return res

    err_msg = f"No items parsed: {str(item_code)}"
    if isinstance(item_code, list):
        res: list[str] = []
        for i in item_code:
            parsed = parse(i)
            if parsed:
                res.append(parsed)
        if len(res) == 0:
            raise ValueError(err_msg)
        return res
    elif isinstance(item_code, (str, int)):
        parsed = parse(item_code)
        if not parsed:
            raise ValueError(err_msg)
        return parsed


def build_headers(headers: dict[str, str]):
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
    items: str | list[str],
    headers: dict[str, str],
    func: Callable[..., Any],
    chunk_size: int,
):
    session = Session()
    session.headers.update(build_headers(headers))

    if isinstance(items, str):
        items = [items]

    items = [str(i) for i in items]
    items = list(set(items))
    items = parse_item_code(items)

    chunks = [items[x : x + chunk_size] for x in range(0, len(items), chunk_size)]
    responses: list[Any] = []
    for chunk in chunks:
        response = func(session, chunk)
        if isinstance(response, list):
            responses += response
        else:
            responses.append(response)
    return responses
