from __future__ import annotations

from ikea_api._api import API
from ikea_api._constants import Constants
from ikea_api.exceptions import IKEAAPIError


class PipItem(API):
    def __init__(self):
        super().__init__(
            f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/products"
        )
        self._session.headers["Accept"] = "*/*"

    def _request_item(self, item_code: str, is_combination: bool):
        prefix = "s" if is_combination else ""
        return self._get(f"{self.endpoint}/{item_code[5:]}/{prefix}{item_code}.json")

    def __call__(self, item_code: str):
        try:
            return self._request_item(item_code, True)
        except IKEAAPIError as exc:
            if not exc.response.status_code == 404:
                raise
            return self._request_item(item_code, False)
