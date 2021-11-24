from __future__ import annotations

import re
from typing import Any

from ikea_api._api import AuthorizedAPI, CustomResponse
from ikea_api._constants import Constants, Secrets
from ikea_api._endpoints.cart import Cart
from ikea_api.exceptions import NoDeliveryOptionsAvailableError, OrderCaptureError


class OrderCapture(AuthorizedAPI):
    def __init__(self, token: str, *, zip_code: str, state_code: str | None = None):
        _validate_zip_code(zip_code)
        _validate_state_code(state_code)
        self._zip_code = zip_code
        self._state_code = state_code

        host = "ikea.ru" if Constants.COUNTRY_CODE == "ru" else "ingka.com"
        super().__init__(
            endpoint=f"https://ordercapture.{host}/ordercaptureapi/{Constants.COUNTRY_CODE}",
            token=token,
        )
        self._session.headers["X-Client-Id"] = Secrets.order_capture_x_client_id

    def _error_handler(self, response: CustomResponse):
        if isinstance(response._json, dict) and "errorCode" in response._json:
            if response._json["errorCode"] in (60005, 60006):
                raise NoDeliveryOptionsAvailableError(response)
            raise OrderCaptureError(response)

    def _get_items_for_checkout(self) -> list[dict[str, str | int]]:
        cart = Cart(self.token).show()
        if not cart["data"].get("cart", {}).get("items"):
            raise RuntimeError("Cannot get items for Order Capture")
        return [
            {
                "quantity": item["quantity"],
                "itemNo": item["itemNo"],
                "uom": item["product"]["unitCode"],
            }
            for item in cart["data"]["cart"]["items"]
        ]

    def _get_checkout(self, items: list[dict[str, str | int]]) -> str:
        """Generate checkout for items"""
        resp: dict[str, str] = self._post(
            f"{self.endpoint}/checkouts",
            headers={"X-Client-Id": Secrets.order_capture_checkout_x_client_id},
            json={
                "channel": "WEBAPP",
                "checkoutType": "STANDARD",
                "shoppingType": "ONLINE",
                "deliveryArea": None,
                "items": items,
                "languageCode": Constants.LANGUAGE_CODE,
            },
        )
        if "resourceId" not in resp:
            raise RuntimeError("No resourceId for checkout")
        return resp["resourceId"]

    def _get_delivery_area(self, checkout: str) -> str:
        """Generate delivery area for checkout from Zip Code and State Code"""
        data = {"enableRangeOfDays": False, "zipCode": self._zip_code}
        if self._state_code is not None:
            data["stateCode"] = self._state_code
        resp: dict[str, str] = self._post(
            f"{self.endpoint}/checkouts/{checkout}/delivery-areas", json=data
        )
        if "resourceId" not in resp:
            raise RuntimeError("No resourceId for delivery area")
        return resp["resourceId"]

    def _get_delivery_services(
        self, checkout: str, delivery_area: str
    ) -> list[dict[str, Any]]:
        """Get available delivery services"""
        return self._get(
            f"{self.endpoint}/checkouts/{checkout}/delivery-areas/{delivery_area}/delivery-services"
        )

    def __call__(self):
        items = self._get_items_for_checkout()
        checkout = self._get_checkout(items)
        delivery_area = self._get_delivery_area(checkout)
        delivery_services = self._get_delivery_services(checkout, delivery_area)
        return delivery_services


def _validate_zip_code(zip_code: str):
    if len(re.findall(r"[^0-9]", zip_code)) > 0:
        raise ValueError(f"Invalid zip code: {zip_code}")


def _validate_state_code(state_code: str | None):
    if state_code is not None:
        if len(state_code) != 2 or len(re.findall(r"[^A-z]+", state_code)) > 0:
            raise ValueError(f"Invalid state code: {state_code}")
