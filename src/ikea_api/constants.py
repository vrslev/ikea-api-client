from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Constants:
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
    base_url: str = "https://www.ikea.com"
    country: str = "ru"
    language: str = "ru"

    @property
    def local_base_url(self) -> str:
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
