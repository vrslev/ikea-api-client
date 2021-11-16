from __future__ import annotations

from datetime import date
from typing import Any, TypedDict


class ChildItemDict(TypedDict):
    item_code: str
    item_name: str | None  # TODO: Rename to name
    weight: float
    qty: int


class ParsedItem(TypedDict):
    is_combination: bool
    item_code: str
    name: str
    image_url: str | None
    weight: float
    child_items: list[ChildItemDict]
    price: int
    url: str
    category_name: str | None
    category_url: str | None


class IngkaItemDict(TypedDict):
    is_combination: bool
    item_code: str
    name: str
    image_url: str | None
    weight: float
    child_items: list[ChildItemDict]


class PipItemDict(TypedDict):
    item_code: str
    price: int
    url: str
    category_name: str | None
    category_url: str | None


class UnavailableItemDict(TypedDict):
    item_code: str
    available_qty: int


class DeliveryOptionDict(TypedDict):
    delivery_date: date | None
    delivery_type: str
    price: int
    service_provider: str | None
    unavailable_items: list[UnavailableItemDict]


class GetDeliveryServicesResponse(TypedDict):
    delivery_options: list[DeliveryOptionDict]
    cannot_add: list[str]


class NoDeliveryOptionsAvailableError(Exception):
    pass


class CostsOrderDict(TypedDict):
    delivery_cost: float
    total_cost: float


class StatusBannerOrderDict(TypedDict):
    purchase_date: str | None
    delivery_date: str | None


class PurchaseHistoryItemDict(TypedDict):
    datetime: str | None
    datetime_formatted: str
    price: float
    purchase_id: int
    status: str
    store: str | None


class PurchaseInfoDict(StatusBannerOrderDict, CostsOrderDict):
    pass


class AddItemsToCartResponse(TypedDict):
    message: dict[str, Any] | None
    cannot_add: list[str]
