from typing import Annotated

from ikea_api._api import API
from ikea_api._constants import Constants, Secrets
from ikea_api.errors import ItemFetchError
from ikea_api.types import CustomResponse


class IngkaItems(API):
    def __init__(self):
        super().__init__(
            f"https://api.ingka.ikea.com/salesitem/communications/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}"
        )
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Referer": f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/order/delivery/",
                "X-Client-Id": Secrets.item_ingka_x_client_id,
            }
        )

    def _error_handler(self, response: CustomResponse):
        if "error" in response._json:
            try:
                item_codes = response._json["error"]["details"][0]["value"]["keys"]
            except (KeyError, TypeError):
                item_codes = None
            raise ItemFetchError(response, item_codes)

    def __call__(self, item_codes: Annotated[list[str], 50]):
        if len(item_codes) > 50:
            raise RuntimeError("Can't get more than 50 items at once")
        return self._get(params={"itemNos": item_codes})
