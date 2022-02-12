from dataclasses import dataclass

from new import abc
from new.error_handlers import handle_401, handle_json_decode_error


@dataclass
class Data:
    item_codes: list[str]


class API(abc.BaseAPI):
    def get_session_info(self):
        headers = self.extend_default_headers(
            {
                "Accept": "*/*",
                "Referer": f"{self.const.base_url}/{self.const.country}/{self.const.language}/order/delivery/",
                "X-Client-Id": "c4faceb6-0598-44a2-bae4-2c02f4019d06",
            }
        )
        url = f"https://api.ingka.ikea.com/salesitem/communications/{self.const.country}/{self.const.language}"
        return abc.SessionInfo(base_url=url, headers=headers)

    @abc.endpoint
    @abc.add_handler(handle_401)
    @abc.add_handler(handle_json_decode_error)
    def get_items(self, data: Data) -> abc.Endpoint[Data, str]:
        request_info = abc.RequestInfo("GET", "", params={"itemNos": data.item_codes})
        response_info = yield request_info
        return response_info.json
