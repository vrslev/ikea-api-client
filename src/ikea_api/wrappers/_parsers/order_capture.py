from __future__ import annotations

from datetime import date, datetime
from typing import Any

from box import Box

from ikea_api.wrappers._parsers import get_box_list
from ikea_api.wrappers.types import DeliveryOptionDict, UnavailableItemDict

DELIVERY_TYPES = {
    "HOME_DELIVERY": "Доставка",
    "PUP": "Пункт самовывоза",
    "PUOP": "Магазин",
    "CLICK_COLLECT_STORE": "Магазин",
    "MOCKED_CLICK_COLLECT_STORE": "Магазин",
    "IBES_CLICK_COLLECT_STORE": "Магазин",
}

SERVICE_TYPES = {"CURBSIDE": " без подъёма", "STANDARD": ""}

SERVICE_PROVIDERS = {
    "DPD": "DPD",
    "BUSINESSLINES": "Деловые линии",
    "russianpost": "Почта России",
}

# pyright: reportUnknownMemberType=false


def parse_delivery_options(options_list: list[dict[str, Any]]):
    return [DeliveryOption(d)() for d in get_box_list(options_list)]


class DeliveryOption:
    def __init__(self, dictionary: Box):
        self.d = dictionary

    def get_delivery_date(self) -> date | None:
        deliveries: list[Box] | None = self.d.deliveries
        if deliveries:
            raw_delivery_time: str | None = deliveries[
                0
            ].selectedTimeWindow.fromDateTime
            if raw_delivery_time:
                return datetime.strptime(
                    raw_delivery_time, "%Y-%m-%dT%H:%M:%S.%f"
                ).date()

    def get_delivery_type(self):
        raw_delivery_type: str = self.d.fulfillmentMethodType
        raw_service_type: str = self.d.servicetype
        service_type: str = SERVICE_TYPES.get(raw_service_type, "")
        return DELIVERY_TYPES.get(raw_delivery_type, raw_delivery_type) + service_type

    def get_price(self):
        price: float = self.d.servicePrice.amount
        return int(price)

    def get_service_provider(self):
        deliveries: list[Box] = self.d.deliveries
        if deliveries:
            pickup_points: list[Box] = deliveries[0].pickUpPoints
            if pickup_points:
                identifier: str | None = pickup_points[0].identifier
                if identifier:
                    for provider, pretty_name in SERVICE_PROVIDERS.items():
                        if provider in identifier:
                            return pretty_name

    def get_unavailable_items(self):
        raw_unavailable_items: list[Box] = self.d.unavailableItems or []
        return [
            UnavailableItemDict(
                item_code=item.itemNo,  # type: ignore
                available_qty=item.availableQuantity,  # type: ignore
            )
            for item in raw_unavailable_items
            if item.itemNo is not None and item.availableQuantity is not None
        ]

    def __call__(self):
        return DeliveryOptionDict(
            delivery_date=self.get_delivery_date(),
            delivery_type=self.get_delivery_type(),
            price=self.get_price(),
            service_provider=self.get_service_provider(),
            unavailable_items=self.get_unavailable_items(),
        )
