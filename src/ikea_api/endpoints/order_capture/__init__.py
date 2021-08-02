from typing import Any, Dict, List, Optional, Union

from ikea_api.api import API
from ikea_api.errors import NoDeliveryOptionsAvailableError, WrongZipCodeError
from ikea_api.utils import validate_zip_code

from ..cart import Cart


class OrderCapture(API):
    """
    API responsible for making an order.
    Use case — check available delivery services.
    """

    def __init__(self, token: str, zip_code: Union[str, int]):
        super().__init__(token, "https://ordercapture.ikea.ru/ordercaptureapi/ru")

        if self._country_code != "ru":
            self._endpoint = "https://ordercapture.ingka.com/ordercaptureapi/{}".format(
                self._country_code
            )

        zip_code = str(zip_code)
        validate_zip_code(zip_code)
        self._zip_code = zip_code

        self._session.headers["X-Client-Id"] = "af2525c3-1779-49be-8d7d-adf32cac1934"

    def __call__(self):
        return self.get_delivery_services()

    def _error_handler(self, status_code: int, response_json: Dict[Any, Any]):
        if "errorCode" in response_json:
            error_code = response_json["errorCode"]
            if error_code == 60004:
                raise WrongZipCodeError
            elif error_code == 60005 or error_code == 60006:
                raise NoDeliveryOptionsAvailableError

    def _get_items_for_checkout_request(self):
        cart = Cart(self._token)
        cart_show = cart.show()
        items_templated: List[Dict[str, Any]] = []
        try:
            if cart_show.get("data"):
                for d in cart_show["data"]["cart"]["items"]:
                    items_templated.append(
                        {
                            "quantity": d["quantity"],
                            "itemNo": d["itemNo"],
                            "uom": d["product"]["unitCode"],
                        }
                    )
        except KeyError:
            pass
        return items_templated

    def _get_checkout(self):
        """Generate checkout for items"""
        items = self._get_items_for_checkout_request()
        if len(items) == 0:
            return

        data = {
            "shoppingType": "ONLINE",
            "channel": "WEBAPP",
            "checkoutType": "STANDARD",
            "languageCode": "ru",
            "items": items,
            "deliveryArea": None,
        }

        response: Dict[str, str] = self._call_api(
            endpoint=f"{self._endpoint}/checkouts",
            headers={"X-Client-Id": "6a38e438-0bbb-4d4f-bc55-eb314c2e8e23"},
            data=data,
        )

        if "resourceId" in response:
            return response["resourceId"]
        raise Exception("No resourceId for checkout")  # TODO: Custom exception

    def _get_delivery_area(self, checkout: Optional[str]):
        """Generate delivery area for checkout from zip code"""
        response = self._call_api(
            endpoint=f"{self._endpoint}/checkouts/{checkout}/delivery-areas",
            data={"zipCode": self._zip_code, "enableRangeOfDays": False},
        )

        if "resourceId" in response:
            return response["resourceId"]
        else:
            raise Exception("No resourceId for delivery area")

    def get_delivery_services(self):
        """Get available delivery services"""
        checkout: Optional[str] = self._get_checkout()
        delivery_area = self._get_delivery_area(checkout)

        response = self._call_api(
            "{}/checkouts/{}/delivery-areas/{}/delivery-services".format(
                self._endpoint, checkout, delivery_area
            )
        )
        return response
