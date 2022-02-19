from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ChildItem(BaseModel):
    name: Optional[str]
    item_code: str
    weight: float
    qty: int


class ParsedItem(BaseModel):
    is_combination: bool
    item_code: str
    name: str
    image_url: Optional[str]
    weight: float
    child_items: List[ChildItem]
    price: int
    url: str
    category_name: Optional[str]
    category_url: Optional[HttpUrl]


class IngkaItem(BaseModel):
    is_combination: bool
    item_code: str
    name: str
    image_url: Optional[str]
    weight: float
    child_items: List[ChildItem]


class PipItem(BaseModel):
    item_code: str
    price: int
    url: str
    category_name: Optional[str]
    category_url: Optional[HttpUrl]


class UnavailableItem(BaseModel):
    item_code: str
    available_qty: int


class DeliveryService(BaseModel):
    is_available: bool
    date: Optional[datetime.date]
    type: str
    price: int
    service_provider: Optional[str]
    unavailable_items: List[UnavailableItem]


class GetDeliveryServicesResponse(BaseModel):
    delivery_options: List[DeliveryService]
    cannot_add: List[str]


class CostsOrder(BaseModel):
    delivery_cost: float
    total_cost: float


class StatusBannerOrder(BaseModel):
    purchase_date: datetime.date
    delivery_date: datetime.date


class PurchaseInfo(StatusBannerOrder, CostsOrder):
    pass


class PurchaseHistoryItem(BaseModel):
    id: str
    status: str
    price: int
    datetime: str
    datetime_formatted: str
    store: str


CannotAddItems = List[str]
