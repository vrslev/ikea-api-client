from __future__ import annotations

from typing import Any

from typing_extensions import Literal

from ikea_api._api import API
from ikea_api.constants import Constants

SearchTypes = Literal["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]


class Search(API):
    def __init__(self):
        super().__init__(
            f"https://sik.search.blue.cdtapps.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/search-result-page",
        )

    def __call__(
        self,
        query: str,
        limit: int = 24,
        types: list[SearchTypes] = [
            "PRODUCT",
            "CONTENT",
            "PLANNER",
            "REFINED_SEARCHES",
            "ANSWER",
        ],
    ) -> dict[str, dict[str, Any] | list[Any]]:
        return self._request(
            method="GET",
            data={
                "autocorrect": "true",
                "subcategories-style": "tree-navigation",
                "types": ",".join(types),
                "q": query,
                "size": limit,
                # API client
                # sr - search results
                # sb - search bar
                "c": "sr",
                "v": "20210322",  # API version
            },
        )
