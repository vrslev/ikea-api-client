from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from ikea_api._constants import Constants
from ikea_api.wrappers import types
from ikea_api.wrappers._parsers import translate_from_dict
from ikea_api.wrappers._parsers.item_base import ItemCode

__all__ = ["main"]

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

SERVICE_TYPES = {
    "ru": {
        "CURBSIDE": "без подъёма",
        "STANDARD": None,
        "EXPRESS": "экспресс",
        "EXPRESS_CURBSIDE": "без подъёма экспресс",
    }
}

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
    pickUpPoints: Optional[List[PickUpPoint]]


class UnavailableItem(BaseModel):
    itemNo: ItemCode
    availableQuantity: int


class ResponseDeliveryService(BaseModel):
    fulfillmentMethodType: str
    servicePrice: Optional[ServicePrice]
    servicetype: str
    deliveries: List[Delivery]
    unavailableItems: Optional[List[UnavailableItem]]


def get_date(deliveries: List[Delivery]):
    for delivery in deliveries:
        if delivery.selectedTimeWindow:
            return delivery.selectedTimeWindow.fromDateTime.date()


def get_type(service: ResponseDeliveryService):
    delivery_type = translate_from_dict(DELIVERY_TYPES, service.fulfillmentMethodType)
    service_type = translate_from_dict(SERVICE_TYPES, service.servicetype)
    if service_type:
        return f"{delivery_type} {service_type}"
    return delivery_type


def get_price(service: ResponseDeliveryService):
    if service.servicePrice:
        return service.servicePrice.amount
    return 0


def get_service_provider(service: ResponseDeliveryService):
    if not (service.deliveries and service.deliveries[0].pickUpPoints):
        return

    identifier = service.deliveries[0].pickUpPoints[0].identifier
    for provider, pretty_name in SERVICE_PROVIDERS.get(
        Constants.LANGUAGE_CODE, {}
    ).items():
        if provider in identifier:
            return pretty_name
    return identifier


def get_unavailable_items(
    unavailable_items: list[UnavailableItem] | None,
) -> list[types.UnavailableItem]:
    if not unavailable_items:
        return []
    return [
        types.UnavailableItem(item_code=i.itemNo, available_qty=i.availableQuantity)
        for i in unavailable_items
    ]


def main(response: list[dict[str, Any]]):
    res: list[types.DeliveryService] = []
    for s in response:
        service = ResponseDeliveryService(**s)
        res.append(
            types.DeliveryService(
                date=get_date(service.deliveries),
                type=get_type(service),
                price=get_price(service),
                service_provider=get_service_provider(service),
                unavailable_items=get_unavailable_items(service.unavailableItems),
            )
        )
    return res
