from dataclasses import dataclass
from typing import Any

from new import abc
from new.constants import Constants, extend_default_headers
from new.error_handlers import handle_401, handle_json_decode_error


def get_session_data(constants: Constants) -> abc.SessionInfo:
    headers = extend_default_headers(
        {
            "Accept": "*/*",
            "Referer": f"{constants.base_url}/{constants.country}/{constants.language}/order/delivery/",
            "X-Client-Id": "c4faceb6-0598-44a2-bae4-2c02f4019d06",
        },
        constants=constants,
    )
    url = f"https://api.ingka.ikea.com/salesitem/communications/{constants.country}/{constants.language}"
    return abc.SessionInfo(base_url=url, headers=headers)


@dataclass
class IngkaItemData:
    item_codes: list[str]


class IngkaItemEndpoint(abc.Endpoint[IngkaItemData, dict[str, Any]]):
    @staticmethod
    def prepare_request(data: IngkaItemData) -> abc.RequestInfo:
        if len(data.item_codes) > 50:
            raise RuntimeError("Can't get more than 50 items at once")
        return abc.RequestInfo(
            method="GET", url="", params={"itemNos": data.item_codes}
        )

    @staticmethod
    def get_error_handlers():
        yield handle_json_decode_error
        yield handle_401

    @staticmethod
    def parse_response(
        response: abc.ResponseInfo[IngkaItemData, Any]
    ) -> dict[str, Any]:
        return response.json


def get_items(item_codes: list[str]):
    return abc.RunInfo(
        get_session_data,
        IngkaItemEndpoint,
        IngkaItemData(item_codes=item_codes),
    )
