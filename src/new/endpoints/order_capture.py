from typing import Any, TypedDict

from new.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from new.constants import Constants, get_auth_header
from new.error_handlers import handle_401, handle_json_decode_error
from new.exceptions import ProcessingError


class CheckoutItem(TypedDict):
    itemNo: str
    quantity: int
    uom: str


class API(BaseAPI):
    token: str

    def __init__(self, constants: Constants, *, token: str) -> None:
        self.token = token
        super().__init__(constants)

    def get_session_info(self) -> SessionInfo:
        host = "ikea.ru" if self.const.country == "ru" else "ingka.com"
        url = f"https://ordercapture.{host}/ordercaptureapi/{self.const.country}"
        headers = self.extend_default_headers(
            {
                "X-Client-Id": "af2525c3-1779-49be-8d7d-adf32cac1934",
                **get_auth_header(self.token),
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_json_decode_error, handle_401])
    def get_checkout(self, items: list[CheckoutItem]) -> EndpointGen[str]:
        """Generate checkout for items"""
        response = yield self.RequestInfo(
            "POST",
            "/checkouts",
            headers={"X-Client-Id": "6a38e438-0bbb-4d4f-bc55-eb314c2e8e23"},
            json={
                "channel": "WEBAPP",
                "checkoutType": "STANDARD",
                "shoppingType": "ONLINE",
                "deliveryArea": None,
                "items": items,
                "languageCode": self.const.language,
                "serviceArea": None,
                "preliminaryAddressInfo": None,
            },
        )
        if "resourceId" not in response.json:
            raise ProcessingError(response, "No id for service area")
        return response.json["resourceId"]

    @endpoint(handlers=[handle_json_decode_error, handle_401])
    def get_service_area(
        self, checkout_id: str, zip_code: str, state_code: str | None = None
    ) -> EndpointGen[str]:
        """Generate delivery area for checkout from Zip Code and State Code"""
        payload = {"zipCode": zip_code}
        if state_code:
            payload["stateCode"] = state_code
        response = yield self.RequestInfo(
            "POST", f"/checkouts/{checkout_id}/service-area", json=payload
        )

        if "id" not in response.json:
            raise ProcessingError(response, "No id for service area")
        return response.json["id"]

    @endpoint(handlers=[handle_json_decode_error, handle_401])
    def get_home_delivery_services(
        self, checkout_id: str, service_area_id: str
    ) -> EndpointGen[dict[str, Any]]:
        """Get available home delivery services"""
        response = yield self.RequestInfo(
            "GET",
            f"/checkouts/{checkout_id}/service-area/{service_area_id}/home-delivery-services",
        )
        return response.json

    @endpoint(handlers=[handle_json_decode_error, handle_401])
    def get_collect_delivery_services(
        self, checkout_id: str, service_area_id: str
    ) -> EndpointGen[dict[str, Any]]:
        """Get available collect delivery services"""
        response = yield self.RequestInfo(
            "GET",
            f"/checkouts/{checkout_id}/service-area/{service_area_id}/collect-delivery-services",
        )
        return response.json


def convert_cart_to_checkout_items(cart_response: dict[str, Any]) -> list[CheckoutItem]:
    if not cart_response["data"].get("cart", {}).get("items"):
        raise RuntimeError("Cannot get items for Order Capture")
    return [
        {
            "quantity": item["quantity"],
            "itemNo": item["itemNo"],
            "uom": item["product"]["unitCode"],
        }
        for item in cart_response["data"]["cart"]["items"]
    ]
