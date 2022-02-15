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

    @property
    def local_base_url(self):
        return f"{self.base_url}/{self.country}/{self.language}"


@lru_cache
def get_default_headers(constants: Constants) -> dict[str, str]:
    return {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": constants.language,
        "Connection": "keep-alive",
        "User-Agent": constants.user_agent,
        "Origin": constants.base_url,
        "Referer": constants.base_url + "/",
    }


def extend_default_headers(
    headers: dict[str, str], constants: Constants
) -> dict[str, str]:
    res = get_default_headers(constants)
    res.update(headers)
    return res


def get_headers_with_token(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + token}
