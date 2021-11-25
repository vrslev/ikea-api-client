from __future__ import annotations

import sys
from typing import Any

from ikea_api._api import API
from ikea_api._constants import Constants

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

SearchType = Literal["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]


class Search(API):
    def __init__(self):
        super().__init__(
            f"https://sik.search.blue.cdtapps.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/search-result-page"
        )

    def __call__(
        self,
        query: str,
        *,
        limit: int = 24,
        types: list[SearchType] = ["PRODUCT"],
    ) -> dict[str, dict[str, Any] | list[Any]]:
        return self._get(
            params={
                "autocorrect": "true",
                "subcategories-style": "tree-navigation",
                "types": ",".join(types),
                "q": query,
                "size": limit,
                "c": "sr",  # API client: sr - search results, sb - search bar
                "v": "20210322",  # API version
            },
        )
