from __future__ import annotations

from typing import Any

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.error_handlers import handle_json_decode_error
from ikea_api.exceptions import ItemFetchError


def build_url(item_code: str, is_combination: bool) -> str:
    prefix = "s" if is_combination else ""
    return f"/{item_code[5:]}/{prefix}{item_code}.json"


class PipItem(BaseIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        url = f"{self._const.local_base_url}/products"
        headers = self._extend_default_headers({"Accept": "*/*"})
        return SessionInfo(base_url=url, headers=headers)

    @endpoint()
    def get_item(
        self, item_code: str, is_combination: bool = True
    ) -> Endpoint[dict[str, Any]]:
        response = yield self._RequestInfo("GET", build_url(item_code, is_combination))

        if response.status_code == 404 and is_combination:
            response = yield self._RequestInfo("GET", build_url(item_code, False))
            if response.status_code == 404:
                raise ItemFetchError(response)

        handle_json_decode_error(response)
        return response.json
