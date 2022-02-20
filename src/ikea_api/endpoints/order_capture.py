from __future__ import annotations

from typing import Any, TypedDict

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseAuthIkeaAPI
from ikea_api.error_handlers import (
    handle_401,
    handle_json_decode_error,
    handle_not_success,
)
from ikea_api.exceptions import ProcessingError


class CheckoutItem(TypedDict):
    itemNo: str
    quantity: int
    uom: str


handlers = (handle_json_decode_error, handle_401, handle_not_success)


class OrderCapture(BaseAuthIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        host = "ikea.ru" if self._const.country == "ru" else "ingka.com"
        url = f"https://ordercapture.{host}/ordercaptureapi/{self._const.country}"
        headers = self._extend_default_headers_with_auth(
            {"X-Client-Id": "af2525c3-1779-49be-8d7d-adf32cac1934"}
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers)
    def get_checkout(self, items: list[CheckoutItem]) -> Endpoint[str]:
        """Generate checkout for items"""
        response = yield self._RequestInfo(
            "POST",
            "/checkouts",
            headers={"X-Client-Id": "6a38e438-0bbb-4d4f-bc55-eb314c2e8e23"},
            json={
                "channel": "WEBAPP",
                "checkoutType": "STANDARD",
                "shoppingType": "ONLINE",
                "deliveryArea": None,
                "items": items,
                "languageCode": self._const.language,
                "serviceArea": None,
                "preliminaryAddressInfo": None,
            },
        )
        if "resourceId" not in response.json:
            raise ProcessingError(response, "No id for service area")
        return response.json["resourceId"]

    @endpoint(handlers)
    def get_service_area(
        self, checkout_id: str, zip_code: str, state_code: str | None = None
    ) -> Endpoint[str]:
        """Generate delivery area for checkout from Zip Code and State Code"""
        payload = {"zipCode": zip_code}
        if state_code:
            payload["stateCode"] = state_code
        response = yield self._RequestInfo(
            "POST", f"/checkouts/{checkout_id}/service-area", json=payload
        )

        if "id" not in response.json:
            raise ProcessingError(response, "No id for service area")
        return response.json["id"]

    @endpoint(handlers)
    def get_home_delivery_services(
        self, checkout_id: str, service_area_id: str
    ) -> Endpoint[dict[str, Any]]:
        """Get available home delivery services"""
        response = yield self._RequestInfo(
            "GET",
            f"/checkouts/{checkout_id}/service-area/{service_area_id}/home-delivery-services",
        )
        return response.json

    @endpoint(handlers)
    def get_collect_delivery_services(
        self, checkout_id: str, service_area_id: str
    ) -> Endpoint[dict[str, Any]]:
        """Get available collect delivery services"""
        response = yield self._RequestInfo(
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
