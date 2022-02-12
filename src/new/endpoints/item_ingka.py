from dataclasses import dataclass

from new.abc import BaseAPI, Endpoint, RequestInfo, SessionInfo, add_handler, endpoint
from new.constants import extend_default_headers
from new.error_handlers import handle_401, handle_json_decode_error


@dataclass
class IngkaItemsData:
    item_codes: list[str]


class IngkaItemsAPI(BaseAPI):
    def get_session_info(self):
        headers = extend_default_headers(
            {
                "Accept": "*/*",
                "Referer": f"{self.constants.base_url}/{self.constants.country}/{self.constants.language}/order/delivery/",
                "X-Client-Id": "c4faceb6-0598-44a2-bae4-2c02f4019d06",
            },
            constants=self.constants,
        )
        url = f"https://api.ingka.ikea.com/salesitem/communications/{self.constants.country}/{self.constants.language}"
        return SessionInfo(base_url=url, headers=headers)

    @endpoint
    @add_handler(handle_401)
    @add_handler(handle_json_decode_error)
    def get_items(self, data: IngkaItemsData) -> Endpoint[IngkaItemsData, str]:
        request_info = RequestInfo("GET", "", params={"itemNos": data.item_codes})
        response_info = yield request_info
        return response_info.json
