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
            if response._json["errorCode"] in (
                60005,  # ISOM_ERROR_NODELSVC
                60006,  # ISOM_ERROR_NOPRODUCTCHOICE
                60013,  # ISOM_ERROR_NOPICKUPPOINT
            ):
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
                "serviceArea": None,
                "preliminaryAddressInfo": None,
            },
        )
        if "resourceId" not in resp:
            raise RuntimeError("No resourceId for checkout")
        return resp["resourceId"]

    def _get_service_area(self, checkout: str) -> str:
        """Generate delivery area for checkout from Zip Code and State Code"""
        data = {"zipCode": self._zip_code}
        if self._state_code is not None:
            data["stateCode"] = self._state_code  # TODO: Test state code
        resp: dict[str, str] = self._post(
            f"{self.endpoint}/checkouts/{checkout}/service-area", json=data
        )
        if "id" not in resp:
            raise RuntimeError("No id for service area")
        return resp["id"]

    def get_home_delivery_services(
        self, checkout_and_service_area: tuple[str, str] | None = None
    ) -> dict[str, Any]:
        """Get available home delivery services"""
        if checkout_and_service_area:
            checkout, service_area = checkout_and_service_area
        else:
            checkout = self._get_checkout(self._get_items_for_checkout())
            service_area = self._get_service_area(checkout)

        return self._get(
            f"{self.endpoint}/checkouts/{checkout}/service-area/{service_area}/home-delivery-services"
        )

    def get_collect_delivery_services(
        self, checkout_and_service_area: tuple[str, str] | None = None
    ) -> dict[str, Any]:
        """Get available collect delivery services"""
        if checkout_and_service_area:
            checkout, service_area = checkout_and_service_area
        else:
            checkout = self._get_checkout(self._get_items_for_checkout())
            service_area = self._get_service_area(checkout)

        return self._get(
            f"{self.endpoint}/checkouts/{checkout}/service-area/{service_area}/collect-delivery-services"
        )


def _validate_zip_code(zip_code: str):
    if len(re.findall(r"[^0-9]", zip_code)) > 0:
        raise ValueError(f"Invalid zip code: {zip_code}")


def _validate_state_code(state_code: str | None):
    if state_code is not None:
        if len(state_code) != 2 or len(re.findall(r"[^A-z]+", state_code)) > 0:
            raise ValueError(f"Invalid state code: {state_code}")
