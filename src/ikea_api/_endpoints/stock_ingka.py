from __future__ import annotations

from ikea_api._api import API, CustomResponse
from ikea_api._constants import Constants, Secrets
from ikea_api.exceptions import ItemFetchError


class IngkaStock(API):
    def __init__(self):
        super().__init__(
            f"https://api.ingka.ikea.com/cia/availabilities/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}"
        )
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Referer": f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/order/delivery/",
                "X-Client-Id": Secrets.stocks_ingka_x_client_id,
            }
        )

    def _error_handler(self, response: CustomResponse):
        if "errors" in response._json:
            try:
                item_code = [response._json["errors"][0]["details"]["itemNo"]]
            except (KeyError, TypeError, IndexError):
                item_code = None
            raise ItemFetchError(response, item_code)

    def __call__(self, item_codes: list[str]):
        return self._get(
            params={
                "itemNos": item_codes,
                "expand": "StoresList,Restocks,SalesLocations",
            }
        )
