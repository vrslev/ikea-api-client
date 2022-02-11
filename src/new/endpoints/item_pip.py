from dataclasses import dataclass
from typing import Any

from new import abc
from new.constants import Constants, extend_default_headers
from new.error_handlers import handle_json_decode_error


def get_session_data(constants: Constants) -> abc.SessionInfo:
    headers = extend_default_headers({"Accept": "*/*"}, constants)
    url = f"{constants.base_url}/{constants.country}/{constants.language}/products"
    return abc.SessionInfo(base_url=url, headers=headers)


@dataclass
class Data:
    item_code: str
    is_combination: bool


def build_url(data: Data):
    prefix = "s" if data.is_combination else ""
    return f"/{data.item_code[5:]}/{prefix}{data.item_code}.json"


def custom_handle_json_decode_error(response: abc.ResponseInfo[Data, Any]):
    if response.status_code == 404 and response.prep_data.is_combination:
        handle_json_decode_error(response)


class Endpoint(abc.Endpoint[Data, dict[str, Any]]):
    @staticmethod
    def prepare_request(data: Data) -> abc.RequestInfo:
        url = build_url(data)
        return abc.RequestInfo(method="GET", url=url)

    @staticmethod
    def get_error_handlers():
        yield custom_handle_json_decode_error

    @staticmethod
    def parse_response(
        response: abc.ResponseInfo[Data, Any]
    ) -> dict[str, Any] | abc.Rerun[Data]:
        if response.status_code == 404 and not response.prep_data.is_combination:
            response.prep_data.is_combination = True
            return abc.Rerun(response.prep_data)

        return response.json


def get_item(item_code: str):
    return abc.RunInfo(get_session_data, Endpoint, Data(item_code, False))
