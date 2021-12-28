from __future__ import annotations

import datetime
from typing import Any, Callable, List, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import HttpUrl
from pydantic.fields import Field, FieldInfo
from pydantic.main import ModelMetaclass as PydanticModelMetaclass

_T = TypeVar("_T")


# https://github.com/microsoft/pyright/blob/main/specs/dataclass_transforms.md#applying-to-pydantic
def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: tuple[type | Callable[..., Any], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


@__dataclass_transform__(kw_only_default=True, field_descriptors=(Field, FieldInfo))
class ModelMetaclass(PydanticModelMetaclass):
    pass


class BaseModel(PydanticBaseModel, metaclass=ModelMetaclass):
    pass


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
