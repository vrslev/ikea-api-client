from __future__ import annotations

import re
from typing import Any, Iterable

from ikea_api.constants import Constants


def get_unshortened_links_from_ingka_pagelinks(  # TODO: Add tests
    message: str,
) -> Iterable[str]:  # TODO: requests agnostic?
    import requests

    session = requests.Session()
    base_url = "https://ingka.page.link/"

    for postfix in re.findall("ingka.page.link/([0-9A-z]+)", message):
        resp = session.get(base_url + postfix, allow_redirects=False)
        location_header = resp.headers.get("Location")
        if location_header is not None:
            yield location_header


def parse_item_codes(
    item_codes: str | list[str], unshorten_ingka_pagelinks: bool = False
) -> list[str]:
    if item_codes == []:
        return []

    if unshorten_ingka_pagelinks:
        if isinstance(item_codes, str):
            item_codes = [item_codes]
        unshortened_links = get_unshortened_links_from_ingka_pagelinks(item_codes[0])
        if unshortened_links:
            item_codes.extend(unshortened_links)

    raw_res: list[str] = re.findall(
        r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_codes)
    )
    regex = re.compile(r"[^0-9]")
    # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
    return list(dict.fromkeys(regex.sub("", i) for i in raw_res))


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
