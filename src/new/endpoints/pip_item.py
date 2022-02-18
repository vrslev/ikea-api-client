from typing import Any

from new.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from new.error_handlers import handle_json_decode_error


def _build_url(item_code: str, is_combination: bool):
    prefix = "s" if is_combination else ""
    return f"/{item_code[5:]}/{prefix}{item_code}.json"


class API(BaseAPI):
    def get_session_info(self) -> SessionInfo:
        url = f"{self.const.local_base_url}/products"
        headers = self.extend_default_headers({"Accept": "*/*"})
        return SessionInfo(base_url=url, headers=headers)

    @endpoint()
    def get_item(
        self, item_code: str, is_combination: bool = True
    ) -> EndpointGen[dict[str, Any]]:
        response = yield self.RequestInfo("GET", _build_url(item_code, is_combination))

        if response.status_code == 404 and is_combination:
            response = yield self.RequestInfo("GET", _build_url(item_code, False))

        handle_json_decode_error(response)
        return response.json
