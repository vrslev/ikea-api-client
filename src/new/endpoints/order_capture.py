from dataclasses import dataclass
from typing import Any, Generator, TypedDict, cast

from new import abc
from new.constants import Constants, get_default_headers, get_headers_with_token


def get_session_info(constants: Constants):
    host = "ikea.ru" if constants.country == "ru" else "ingka.com"
    url = f"https://ordercapture.{host}/ordercaptureapi/{constants.country}"
    headers = get_default_headers(constants=constants)
    headers.update({"X-Client-Id": "af2525c3-1779-49be-8d7d-adf32cac1934"})
    return abc.SessionInfo(base_url=url, headers=headers)


class CheckoutItem(TypedDict):
    quantity: int
    itemNo: str
    uom: str


@dataclass
class CheckoutData:
    token: str
    items: list[CheckoutItem]


class CheckoutResponse(TypedDict):
    resourceId: str


class Checkout(abc.Endpoint[CheckoutData, CheckoutResponse]):
    @staticmethod
    def prepare_request(data: CheckoutData):
        headers = get_headers_with_token(data.token)
        headers["X-Client-Id"] = "6a38e438-0bbb-4d4f-bc55-eb314c2e8e23"

        return abc.RequestInfo(
            method="POST",
            url="/checkouts",
            headers=headers,
            json={
                "channel": "WEBAPP",
                "checkoutType": "STANDARD",
                "shoppingType": "ONLINE",
                "deliveryArea": None,
                "items": data.items,
                "languageCode": Constants.language,  # TODO
                "serviceArea": None,
                "preliminaryAddressInfo": None,
            },
        )

    @staticmethod
    def parse_response(response: abc.ResponseInfo[CheckoutData, Any]):
        return cast(CheckoutResponse, response.json)


@dataclass
class ServiceAreaData:
    token: str
    checkout: str
    zip_code: str
    state_code: str | None = None


class ServiceAreaResponse(TypedDict):
    id: str


class ServiceArea(abc.Endpoint[ServiceAreaData, ServiceAreaResponse]):
    @staticmethod
    def prepare_request(data: ServiceAreaData):
        payload = {"zipCode": data.zip_code}
        if data.state_code is not None:
            payload["stateCode"] = data.state_code

        return abc.RequestInfo(
            method="POST",
            url="/service-area",
            json=payload,
            headers=get_headers_with_token(data.token),
        )

    @staticmethod
    def parse_response(response: abc.ResponseInfo[ServiceAreaData, Any]):
        return cast(ServiceAreaResponse, response.json)


def just_get(
    token: str, items: list[CheckoutItem], zip_code: str
) -> Generator[abc.RunInfo[Any, Any], Any, ServiceAreaResponse]:
    checkout: CheckoutResponse = yield abc.RunInfo(
        get_session_info, Checkout, CheckoutData(token=token, items=items)
    )
    service_area: ServiceAreaResponse = yield abc.RunInfo(
        get_session_info,
        ServiceArea,
        ServiceAreaData(
            token=token, checkout=checkout["resourceId"], zip_code=zip_code
        ),
    )
    return service_area
