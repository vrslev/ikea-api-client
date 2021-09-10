from __future__ import annotations

from typing import Any
from ikea_api.api import API, Method
from ikea_api.constants import Constants


class Search(API):
    def __init__(self):
        super().__init__(
            token="",
            endpoint=f"https://sik.search.blue.cdtapps.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/search-result-page",
        )

    def __call__(self, query: str, amount: int = 24) -> list[dict[str, Any]]:
        return self._search(query, amount)

    def _search(self, query: str, amount: int) -> list[dict[str, Any]]:
        """search the product catalog from a query, returning a specific amount of search results (24 is the default amount of search results)"""
        if amount <= 0:
            raise ValueError("The parameter 'amount' must be > 0")

        params = {
            "autocorrect": "true",
            "subcategories-style": "tree-navigation",
            "types": "PRODUCT",
            "q": query,
            "size": amount,
            "c": "sr",
        }

        response = self._call_api(data=params, method=Method.GET)

        return response["searchResultPage"]["products"]["main"]["items"]
