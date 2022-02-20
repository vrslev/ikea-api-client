from __future__ import annotations

from typing import Any, Dict

from ikea_api.abc import Endpoint, RequestInfo, ResponseInfo, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.exceptions import ItemFetchError, WrongItemCodeError

ItemCodeToComboDict = Dict[str, bool]


def _build_url(items: ItemCodeToComboDict) -> str:
    return ";".join(
        f"{'SPR' if is_combintaion else 'ART'},{item_code}"
        for item_code, is_combintaion in items.items()
    )


class IowsItems(BaseIkeaAPI):
    items: ItemCodeToComboDict

    def _get_session_info(self) -> SessionInfo:
        url = f"https://iows.ikea.com/retail/iows/{self._const.country}/{self._const.language}/catalog/items/"
        headers = self._extend_default_headers(
            {
                "Accept": "application/vnd.ikea.iows+json;version=2.0",
                "Referer": f"{self._const.local_base_url}/shoppinglist/",
                "consumer": "MAMMUT#ShoppingCart",
                "contract": "37249",
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    def _build_request(self) -> RequestInfo:
        return self._RequestInfo("GET", _build_url(self.items))

    def _handle_response(
        self, response: ResponseInfo, relapse: int
    ) -> list[dict[str, Any]] | None:
        if response.status_code == 404 and len(self.items) == 1:
            if relapse != 0:
                raise WrongItemCodeError(response)

            item_code = list(self.items.keys())[0]
            self.items[item_code] = not self.items[item_code]
            return

        if not response.text:
            return

        if "ErrorList" not in response.json or relapse == 2:
            if "RetailItemCommList" in response.json:
                return response.json["RetailItemCommList"]["RetailItemComm"]
            return [response.json["RetailItemComm"]]

        errors: list[dict[str, Any]] | dict[str, Any] = response.json["ErrorList"][
            "Error"
        ]
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

    @endpoint()
    def get_items(self, item_codes: list[str]) -> Endpoint[list[dict[str, Any]]]:
        self.items = {i: False for i in item_codes}

        for relapse in range(3):
            response = yield self._build_request()
            data = self._handle_response(response, relapse)
            if data is not None:
                return data

        raise NotImplementedError
