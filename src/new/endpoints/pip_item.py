from typing import Any

from new import abc
from new.error_handlers import handle_json_decode_error


def _build_url(item_code: str, is_combination: bool):
    prefix = "s" if is_combination else ""
    return f"/{item_code[5:]}/{prefix}{item_code}.json"


class API(abc.BaseAPI):
    def get_session_info(self) -> abc.SessionInfo:
        url = f"{self.const.local_base_url}/products"
        headers = self.extend_default_headers({"Accept": "*/*"})
        return abc.SessionInfo(base_url=url, headers=headers)

    def get_item(
        self, item_code: str, is_combination: bool = True
    ) -> abc.EndpointGen[dict[str, Any]]:
        response_info = yield abc.RequestInfo(
            "GET", _build_url(item_code, is_combination)
        )

        if response_info.status_code == 404 and is_combination:
            return (yield from self.get_item(item_code=item_code, is_combination=False))

        handle_json_decode_error(response_info)
        return response_info.json
