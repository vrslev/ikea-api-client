from __future__ import annotations

from typing import Any

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.error_handlers import (
    handle_401,
    handle_json_decode_error,
    handle_not_success,
)
from ikea_api.exceptions import ItemFetchError


class IngkaItems(BaseIkeaAPI):
    def _get_session_info(self):
        headers = self._extend_default_headers(
            {
                "Accept": "*/*",
                "Referer": f"{self._const.local_base_url}/order/delivery/",
                "X-Client-Id": "c4faceb6-0598-44a2-bae4-2c02f4019d06",
            }
        )
        url = f"https://api.ingka.ikea.com/salesitem/communications/{self._const.country}/{self._const.language}"
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_json_decode_error, handle_401, handle_not_success])
    def get_items(self, item_codes: list[str]) -> Endpoint[dict[str, Any]]:
        response = yield self._RequestInfo("GET", params={"itemNos": item_codes})

        if "error" in response.json:
            try:
                msg = response.json["error"]["details"][0]["value"]["keys"]
            except (KeyError, TypeError, IndexError):
                msg = None
            raise ItemFetchError(response, msg)

        return response.json
