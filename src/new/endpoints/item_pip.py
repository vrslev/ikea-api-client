from typing import Any

from new import abc
from new.error_handlers import handle_json_decode_error


def _build_url(item_code: str, is_combination: bool):
    prefix = "s" if is_combination else ""
    return f"/{item_code[5:]}/{prefix}{item_code}.json"


class API(abc.BaseAPI):
    def get_session_info(self) -> abc.SessionInfo:
        url = (
            f"{self.const.base_url}/{self.const.country}/{self.const.language}/products"
        )
        headers = self.extend_default_headers({"Accept": "*/*"})
        return abc.SessionInfo(base_url=url, headers=headers)

    def get_item(
        self, item_code: str, is_combination: bool = False
    ) -> abc.Endpoint[dict[str, Any]]:
        request_info = abc.RequestInfo(
            method="GET", url=_build_url(item_code, is_combination)
        )
        response_info = yield request_info
        if response_info.status_code == 404 and not is_combination:
            if not is_combination:
                yield from self.get_item(item_code=item_code, is_combination=True)

            handle_json_decode_error(response_info)

        return response_info.json
