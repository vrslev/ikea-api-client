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

#
# Shared
#


class SolutionPrice(BaseModel):
    inclTax: int


class EarliestPossibleSlot(BaseModel):
    fromDateTime: datetime


class TimeWindows(BaseModel):
    # TODO: Check if this is the same for home delivery services
    earliestPossibleSlot: Optional[EarliestPossibleSlot]


class HomeDelivery(BaseModel):
    type: str
    timeWindows: Optional[TimeWindows]


class UnavailableItem(BaseModel):
    itemNo: ItemCode
    availableQuantity: int


def get_date(deliveries: list[HomeDelivery] | list[PickUpPoint] | None):
    if not deliveries:
        return

    for delivery in deliveries:
        if delivery.timeWindows and delivery.timeWindows.earliestPossibleSlot:
            return delivery.timeWindows.earliestPossibleSlot.fromDateTime


def get_type(service: HomeDeliveryService | CollectDeliveryService):
    delivery_type = translate_from_dict(DELIVERY_TYPES, service.fulfillmentMethodType)
    if service.solution:
        service_type = translate_from_dict(SERVICE_TYPES, service.solution)
        if service_type:
            return f"{delivery_type} {service_type}"
    return delivery_type


def get_price(service: HomeDeliveryService | CollectDeliveryService):
    if service.solutionPrice:
        return service.solutionPrice.inclTax
    return 0


def get_unavailable_items(
    service: HomeDeliveryService | CollectDeliveryService,
) -> list[types.UnavailableItem]:
    if not service.unavailableItems:
        return []
    return [
        types.UnavailableItem(item_code=i.itemNo, available_qty=i.availableQuantity)
        for i in service.unavailableItems
    ]


#
# Home Delivery Services
#


class HomePossibleDeliveries(BaseModel):
    deliveries: List[HomeDelivery]


class HomeDeliveryService(BaseModel):
    fulfillmentMethodType: str
    solution: Optional[str]  # TODO: Optional or not?
    solutionPrice: Optional[SolutionPrice]
    possibleDeliveries: HomePossibleDeliveries
    unavailableItems: Optional[List[UnavailableItem]]


class HomePossibleDeliveryServices(BaseModel):
    deliveryServices: List[HomeDeliveryService]


class HomeDeliveryServicesResponse(BaseModel):
    possibleDeliveryServices: HomePossibleDeliveryServices


def parse_home_delivery_services(response: dict[str, Any]):
    parsed_response = HomeDeliveryServicesResponse(**response)
    res: list[types.DeliveryService] = []
    for service in parsed_response.possibleDeliveryServices.deliveryServices:
        if not service.possibleDeliveries.deliveries:
            continue

        res.append(
            types.DeliveryService(
                date=get_date(service.possibleDeliveries.deliveries),
                type=get_type(service),
                price=get_price(service),
                service_provider=None,
                unavailable_items=get_unavailable_items(service),
            )
        )
    return res


#
# Collect Delivery Services
#


class PickUpPoint(BaseModel):
    timeWindows: Optional[TimeWindows]
    identifier: Optional[str]


class PossiblePickUpPoints(BaseModel):
    pickUpPoints: List[PickUpPoint]


class CollectDelivery(BaseModel):
    type: str
    possiblePickUpPoints: PossiblePickUpPoints


class CollectPossibleDeliveries(BaseModel):
    deliveries: List[CollectDelivery]


class CollectDeliveryService(BaseModel):
    fulfillmentMethodType: str
    solution: Optional[str]
    solutionPrice: Optional[SolutionPrice]
    possibleDeliveries: Optional[CollectPossibleDeliveries]
    unavailableItems: Optional[List[UnavailableItem]]


class CollectPossibleDeliveryServices(BaseModel):
    deliveryServices: List[CollectDeliveryService]


class CollectDeliveryServicesResponse(BaseModel):
    possibleDeliveryServices: CollectPossibleDeliveryServices


def get_service_provider(pickup_point: PickUpPoint):
    identifier = pickup_point.identifier
    if not identifier:
        return
    for provider, pretty_name in SERVICE_PROVIDERS.get(
        Constants.LANGUAGE_CODE, {}
    ).items():
        if provider in identifier:
            return pretty_name
    return identifier


def parse_collect_delivery_services(response: dict[str, Any]):
    parsed_response = CollectDeliveryServicesResponse(**response)
    res: list[types.DeliveryService] = []

    for service in parsed_response.possibleDeliveryServices.deliveryServices:
        if not service.possibleDeliveries:
            continue
        if not service.possibleDeliveries.deliveries:
            continue

        pickup_points = service.possibleDeliveries.deliveries[
            0
        ].possiblePickUpPoints.pickUpPoints
        if not pickup_points:
            continue

        pickup_point = pickup_points[0]
        if not pickup_point.timeWindows:
            continue
        if not pickup_point.timeWindows.earliestPossibleSlot:
            continue

        res.append(
            types.DeliveryService(
                date=pickup_point.timeWindows.earliestPossibleSlot.fromDateTime,
                type=get_type(service),
                price=get_price(service),
                service_provider=get_service_provider(pickup_point),
                unavailable_items=get_unavailable_items(service),
            )
        )

    return res


def main(
    *,
    home_delivery_services_response: dict[str, Any],
    collect_delivery_services_response: dict[str, Any],
) -> list[types.DeliveryService]:
    return parse_home_delivery_services(
        home_delivery_services_response
    ) + parse_collect_delivery_services(collect_delivery_services_response)
