from __future__ import annotations

from typing import Any

from ikea_api.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from ikea_api.error_handlers import handle_json_decode_error
from ikea_api.exceptions import ItemFetchError


class API(BaseAPI):
    def get_session_info(self) -> SessionInfo:
        url = f"https://api.ingka.ikea.com/cia/availabilities/{self.const.country}/{self.const.language}"
        headers = self.extend_default_headers(
            {
                "Accept": "*/*",
                "Referer": f"{self.const.local_base_url}/order/delivery/",
                "X-Client-Id": "b6c117e5-ae61-4ef5-b4cc-e0b1e37f0631",
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_json_decode_error])
    def get_stock(self, item_codes: list[str]) -> EndpointGen[dict[str, Any]]:
        params = {"itemNos": item_codes, "expand": "StoresList,Restocks,SalesLocations"}
        response = yield self.RequestInfo("GET", "", params=params)

        if "errors" not in response.json:
            return response.json

        try:
            item_code = response.json["errors"][0]["details"]["itemNo"]
        except (KeyError, TypeError, IndexError):
            item_code = None
        raise ItemFetchError(response, msg=item_code)
