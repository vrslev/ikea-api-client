from __future__ import annotations

from typing import Any

from requests import Response

from ikea_api._api import API
from ikea_api._constants import Constants, Secrets
from ikea_api.exceptions import ItemFetchError


class IowsItems(API):
    """IOWS Item API. Works only for Russian market"""

    def __init__(self):
        super().__init__("https://iows.ikea.com/retail/iows/ru/ru/catalog/items/")
        self._session.headers.update(
            {
                "Accept": "application/vnd.ikea.iows+json;version=2.0",
                "Referer": f"{Constants.BASE_URL}/ru/ru/shoppinglist/",
                "consumer": Secrets.item_iows_consumer,
                "contract": Secrets.item_iows_contract,
            }
        )

    def _set_initial_items(self, item_codes: list[str]):
        self.items = {i: False for i in item_codes}  # item_code: is_combination

    def _build_payload(self, items: dict[str, bool]):
        return ";".join(
            f"{'SPR' if is_combintaion else 'ART'},{item_code}"
            for item_code, is_combintaion in items.items()
        )

    def _get_response(self, relapse: int = 0) -> Response:
        endpoint = f"{self.endpoint}{self._build_payload(self.items)}"
        response = self._session.get(endpoint)

        if (
            response.status_code == 404
        ):  # 404 only happens when something is really wrong or when it is wrong item code
            if len(self.items) == 1:
                if relapse == 0:
                    # Single item code with wrong item type
                    item_code = list(self.items.keys())[0]
                    self.items[item_code] = not self.items[item_code]
                    return self._get_response(relapse + 1)
                else:
                    raise ItemFetchError(response, "Wrong Item Code")

        if not response.text:
            return response

        return self._handle_response(response, relapse)

    def _handle_response(self, response: Response, relapse: int) -> Response:  # type: ignore
        r_json = response.json()

        if "ErrorList" not in r_json or relapse == 2:
            return response

        errors: list[dict[str, Any]] | dict[str, Any] = r_json["ErrorList"]["Error"]
        if isinstance(errors, dict):
            errors = [errors]

        for err in errors:
            if err.get("ErrorCode", {}).get("$") != 1101:
                # Not error with item type
                raise ItemFetchError(response, err)

            err_list: dict[str, Any] = {
                attr["Name"]["$"]: attr["Value"]["$"]
                for attr in err["ErrorAttributeList"]["ErrorAttribute"]
            }
            item_code = str(err_list["ITEM_NO"])
            if relapse == 0:  # Probably wrong item type: try to switch it
                self.items[item_code] = err_list["ITEM_TYPE"] == "ART"
            else:  # Nope, item is invalid
                del self.items[item_code]

        return self._get_response(relapse + 1)

    def __call__(self, item_codes: list[str]) -> list[Any]:
        if len(item_codes) > 90:
            raise RuntimeError("Can't get more than 90 items at once")

        self._set_initial_items(item_codes)
        resp = self._get_response()

        if not resp.text:
            return []

        data: dict[str, Any] = resp.json()

        if "RetailItemCommList" in data:
            return data["RetailItemCommList"]["RetailItemComm"]
        return [data["RetailItemComm"]]
