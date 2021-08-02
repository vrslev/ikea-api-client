from requests import Session

from ...constants import Constants
from ...utils import get_config_values, parse_item_code

config = get_config_values()
country_code, language_code = config["country_code"], config["language_code"]


class ItemFetchError(Exception):
    pass


def build_headers(headers):
    new_headers = {
        "Origin": Constants.BASE_URL,
        "User-Agent": Constants.USER_AGENT,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": language_code,
        "Connection": "keep-alive",
    }
    new_headers.update(headers)
    return new_headers


def generic_item_fetcher(items, headers, function, chunk_size):
    session = Session()
    session.headers.update(build_headers(headers))

    if isinstance(items, str):
        items = [items]
    elif not isinstance(items, list):
        raise TypeError("String or list required")

    items = [str(i) for i in items]
    items = list(set(items))
    items: list[str] = parse_item_code(items)  # pyright: reportGeneralTypeIssues=false

    chunks = [items[x : x + chunk_size] for x in range(0, len(items), chunk_size)]
    responses = []
    for chunk in chunks:
        response = function(session, chunk)
        if isinstance(response, list):
            responses += response
        else:
            responses.append(response)
    return responses
