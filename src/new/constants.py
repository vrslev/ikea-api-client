from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Constants:
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15"
        + " (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
    )
    base_url: str = "https://www.ikea.com"
    language: str = "ru"
    country: str = "ru"


class Secrets:
    item_iows_consumer = "MAMMUT#ShoppingCart"
    item_iows_contract = "37249"
    order_capture_x_client_id = "af2525c3-1779-49be-8d7d-adf32cac1934"
    order_capture_checkout_x_client_id = "6a38e438-0bbb-4d4f-bc55-eb314c2e8e23"
    auth_guest_token_x_client_id = "e026b58d-dd69-425f-a67f-1e9a5087b87b"  # nosec
    auth_guest_token_x_client_secret = (  # nosec
        "cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB"
    )


@lru_cache
def get_default_headers(constants: Constants):
    return {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": constants.language,
        "Connection": "keep-alive",
        "User-Agent": constants.user_agent,
        "Origin": constants.base_url,
        "Referer": constants.base_url + "/",
    }


def extend_default_headers(headers: dict[str, str], constants: Constants):
    res = get_default_headers(constants)
    res.update(headers)
    return res


def get_headers_with_token(token: str):
    return {"Authorization": "Bearer " + token}
