from typing import Any

from new.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from new.error_handlers import handle_401, handle_json_decode_error


class API(BaseAPI):
    def get_session_info(self):
        headers = self.extend_default_headers(
            {
                "Accept": "*/*",
                "Referer": f"{self.const.local_base_url}/order/delivery/",
                "X-Client-Id": "c4faceb6-0598-44a2-bae4-2c02f4019d06",
            }
        )
        url = f"https://api.ingka.ikea.com/salesitem/communications/{self.const.country}/{self.const.language}"
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_401, handle_json_decode_error])
    def get_items(self, item_codes: list[str]) -> EndpointGen[dict[str, Any]]:
        response = yield self.RequestInfo("GET", "", params={"itemNos": item_codes})
        return response.json
