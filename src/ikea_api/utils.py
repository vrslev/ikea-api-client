from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any, Iterable, Optional, cast

from ikea_api.constants import Constants

if TYPE_CHECKING:
    import httpx


def parse_item_codes(item_codes: list[str] | str) -> list[str]:
    raw_res: list[str] = re.findall(
        r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_codes)
    )
    regex = re.compile(r"[^0-9]")
    # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
    return list(dict.fromkeys(regex.sub("", i) for i in raw_res))


def _parse_ingka_pagelink_urls(message: str) -> Iterable[str]:
    base_url = "https://ingka.page.link/"
    postfixes = re.findall("ingka.page.link/([0-9A-z]+)", message)
    for postfix in postfixes:
        yield base_url + postfix


def _get_location_headers(responses: Iterable[httpx.Response]) -> list[str]:
    res: list[str] = []
    for response in responses:
        location = cast(Optional[str], response.headers.get("Location"))  # type: ignore
        if location is not None:
            res.append(location)
    return res


async def unshorten_urls_from_ingka_pagelinks(message: str) -> list[str]:
    import httpx

    client = httpx.AsyncClient()
    urls = _parse_ingka_pagelink_urls(message)
    coros = (client.get(url, follow_redirects=False) for url in urls)  # type: ignore
    responses = await asyncio.gather(*coros)
    return _get_location_headers(responses)


def format_item_code(item_code: str) -> str | None:
    matches = parse_item_codes(item_code)
    if not matches:
        return None
    item_code = matches[0]
    return item_code[0:3] + "." + item_code[3:6] + "." + item_code[6:8]


def translate_from_dict(
    constants: Constants, dictionary: dict[str, dict[str, Any]], v: str
) -> str:
    lang_dict = dictionary.get(constants.language)
    if lang_dict is None:
        return v
    return lang_dict.get(v, v)
