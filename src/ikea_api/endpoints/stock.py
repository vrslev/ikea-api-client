from __future__ import annotations

from typing import Any

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.error_handlers import handle_graphql_error, handle_json_decode_error


class Stock(BaseIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        url = f"https://api.ingka.ikea.com/cia/availabilities/ru/{self._const.country}"
        headers = self._extend_default_headers(
            {
                "Accept": "application/json;version=2",
                "Referer": "https://www.ikea.com/",
                "X-Client-Id": "b6c117e5-ae61-4ef5-b4cc-e0b1e37f0631",
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_json_decode_error, handle_graphql_error])
    def get_stock(self, item_code: str) -> Endpoint[dict[str, Any]]:
        params = {
            "itemNos": [item_code],
            "expand": "StoresList,Restocks,SalesLocations",
        }
        response = yield self._RequestInfo("GET", params=params)
        return response.json
