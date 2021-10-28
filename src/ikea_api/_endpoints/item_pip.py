from ikea_api._api import API
from ikea_api.constants import Constants
from ikea_api.errors import IkeaApiError


class ItemPip(API):
    def __init__(self):
        super().__init__(
            f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/products"
        )
        self._session.headers["Accept"] = "*/*"

    def _request_item(self, item_code: str, is_combination: bool):
        prefix = "s" if is_combination else ""
        return self._request(
            f"{self.endpoint}/{item_code[5:]}/{prefix}{item_code}.json", method="GET"
        )

    def __call__(self, item_code: str):
        try:
            return self._request_item(item_code, True)
        except IkeaApiError as exc:
            if not exc.args[0] == 404:
                raise
            return self._request_item(item_code, False)
