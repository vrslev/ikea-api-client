from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from ikea_api._constants import Constants
from ikea_api.wrappers._parsers import translate
from ikea_api.wrappers._parsers.item_base import ItemCode
from ikea_api.wrappers.types import DeliveryServiceDict, UnavailableItemDict

DELIVERY_TYPES = {
    "ru": {
        "HOME_DELIVERY": "Доставка",
        "PUP": "Пункт самовывоза",
        "PUOP": "Магазин",
        "CLICK_COLLECT_STORE": "Магазин",
        "MOCKED_CLICK_COLLECT_STORE": "Магазин",
        "IBES_CLICK_COLLECT_STORE": "Магазин",
    }
}

SERVICE_TYPES = {"ru": {"CURBSIDE": "без подъёма", "STANDARD": None}}

SERVICE_PROVIDERS = {
    "ru": {
        "DPD": "DPD",
        "BUSINESSLINES": "Деловые линии",
        "russianpost": "Почта России",
    }
}


class ServicePrice(BaseModel):
    amount: int


class SelectedTimeWindow(BaseModel):
    fromDateTime: datetime


class PickUpPoint(BaseModel):
    identifier: str


class Delivery(BaseModel):
    type: str
    selectedTimeWindow: Optional[SelectedTimeWindow]
    pickUpPoints: Optional[list[PickUpPoint]]


class UnavailableItem(BaseModel):
    itemNo: ItemCode
    availableQuantity: int


class DeliveryService(BaseModel):
    fulfillmentMethodType: str
    servicePrice: Optional[ServicePrice]
    servicetype: str
    deliveries: list[Delivery]
    unavailableItems: Optional[list[UnavailableItem]]


def get_date(deliveries: list[Delivery]):
    for delivery in deliveries:
        if delivery.selectedTimeWindow:
            return delivery.selectedTimeWindow.fromDateTime.date()


def get_type(service: DeliveryService):
    delivery_type = translate(DELIVERY_TYPES, service.fulfillmentMethodType)
    if service_type := translate(SERVICE_TYPES, service.servicetype):
        return f"{delivery_type} {service_type}"
    return delivery_type


def get_price(service: DeliveryService):
    if service.servicePrice:
        return service.servicePrice.amount
    return 0


def get_service_provider(service: DeliveryService):
    if not (service.deliveries and service.deliveries[0].pickUpPoints):
        return

    identifier = service.deliveries[0].pickUpPoints[0].identifier
    for provider, pretty_name in SERVICE_PROVIDERS[Constants.LANGUAGE_CODE].items():
        if provider in identifier:
            return pretty_name
    return identifier


def get_unavailable_items(
    unavailable_items: list[UnavailableItem] | None,
) -> list[UnavailableItemDict]:
    if not unavailable_items:
        return []
    return [
        UnavailableItemDict(item_code=i.itemNo, available_qty=i.availableQuantity)
        for i in unavailable_items
    ]


def main(response: list[dict[str, Any]]):
    for s in response:
        service = DeliveryService(**s)
        yield DeliveryServiceDict(
            date=get_date(service.deliveries),
            type=get_type(service),
            price=get_price(service),
            service_provider=get_service_provider(service),
            unavailable_items=get_unavailable_items(service.unavailableItems),
        )
