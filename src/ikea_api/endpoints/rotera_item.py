from __future__ import annotations

from typing import Any

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.error_handlers import handle_json_decode_error
from ikea_api.exceptions import ItemFetchError


def build_url(item_code: str) -> str:
    return f"/{item_code}.json"


class RoteraItem(BaseIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        url = f"{self._const.base_url}/global/assets/rotera/resources"
        headers = self._extend_default_headers({"Accept": "*/*"})
        return SessionInfo(base_url=url, headers=headers)

    @endpoint()
    def get_item(self, item_code: str) -> Endpoint[dict[str, Any]]:
        response = yield self._RequestInfo("GET", build_url(item_code))

        if response.status_code == 404:
            raise ItemFetchError(response)

        handle_json_decode_error(response)
        return response.json
