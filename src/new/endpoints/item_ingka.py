from dataclasses import dataclass

from new import abc
from new.constants import extend_default_headers
from new.error_handlers import handle_401, handle_json_decode_error


@dataclass
class IngkaItemsData:
    item_codes: list[str]


class IngkaItemsAPI(abc.BaseAPI):
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
        return abc.SessionInfo(base_url=url, headers=headers)

    @abc.add_handler(handle_401)
    @abc.add_handler(handle_json_decode_error)
    def get_items(self, data: IngkaItemsData) -> abc.Endpoint[IngkaItemsData, str]:
        request_info = abc.RequestInfo("GET", "", params={"itemNos": data.item_codes})
        response_info = yield request_info
        return response_info.json
