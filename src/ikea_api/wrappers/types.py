from __future__ import annotations

import datetime
from typing import Any, Callable, Optional, TypedDict, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from pydantic.main import ModelMetaclass as PydanticModelMetaclass

# TODO: Make all of this Pydantic models
_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: tuple[type | Callable[..., Any], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


@__dataclass_transform__(kw_only_default=True, field_descriptors=(Field,))
class ModelMetaclass(PydanticModelMetaclass):
    pass


class BaseModel(PydanticBaseModel, metaclass=ModelMetaclass):
    pass


class ChildItem(BaseModel):
    name: str | None
    item_code: str
    weight: float
    qty: int


class ParsedItem(TypedDict):
    is_combination: bool
    item_code: str
    name: str
    image_url: str | None
    weight: float
    child_items: list[ChildItem]
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
    child_items: list[ChildItem]


class PipItemDict(TypedDict):
    item_code: str
    price: int
    url: str
    category_name: str | None
    category_url: str | None


class UnavailableItemDict(TypedDict):
    item_code: str
    available_qty: int


class DeliveryServiceDict(TypedDict):
    date: datetime.date | None
    type: str
    price: int
    service_provider: str | None
    unavailable_items: list[UnavailableItemDict]


class GetDeliveryServicesResponse(TypedDict):
    delivery_options: list[DeliveryServiceDict]
    cannot_add: list[str]


class NoDeliveryOptionsAvailableError(Exception):
    pass


class CostsOrderDict(TypedDict):
    delivery_cost: float
    total_cost: float


class StatusBannerOrderDict(BaseModel):
    purchase_date: datetime.date
    delivery_date: datetime.date


class PurchaseHistoryItemDict(BaseModel):
    id: str
    status: str
    price: int
    datetime: str
    datetime_formatted: str
    store: str


# class PurchaseInfoDict(StatusBannerOrderDict, CostsOrderDict):
class PurchaseInfoDict:
    pass


class AddItemsToCartResponse(TypedDict):
    message: dict[str, Any] | None
    cannot_add: list[str]
