from datetime import date
from typing import Any, Optional

from pydantic import BaseModel

from ikea_api.wrappers._parsers import translate
from ikea_api.wrappers.types import (
    CostsOrderDict,
    PurchaseHistoryItemDict,
    StatusBannerOrderDict,
)

STORE_NAMES = {"ru": {"IKEA": "Интернет-магазин", "Санкт-Петербург: Парнас": "Парнас"}}


class DateAndTime(BaseModel):
    date: date


class DeliveryDate(BaseModel):
    estimatedFrom: DateAndTime


class DeliveryMethod(BaseModel):
    deliveryDate: DeliveryDate


class StatusBannerOrder(BaseModel):
    dateAndTime: DateAndTime
    deliveryMethods: list[DeliveryMethod]


class StatusBannerData(BaseModel):
    order: StatusBannerOrder


class StatusBannerResponse(BaseModel):
    data: StatusBannerData


class Cost(BaseModel):
    value: int


class CostsOrderCosts(BaseModel):
    delivery: Cost
    total: Cost


class CostsOrder(BaseModel):
    costs: CostsOrderCosts


class CostsData(BaseModel):
    order: CostsOrder


class CostsResponse(BaseModel):
    data: CostsData


class HistoryDateAndTime(BaseModel):
    date: str
    time: str
    formattedLongDateTime: str


class HistoryTotalCost(BaseModel):
    value: Optional[int]


class HistoryItem(BaseModel):
    id: str
    status: str
    storeName: str
    dateAndTime: HistoryDateAndTime
    totalCost: HistoryTotalCost


class HistoryData(BaseModel):
    history: list[HistoryItem]


class History(BaseModel):
    data: HistoryData


def parse_status_banner_order(response: dict[str, Any]):
    order = StatusBannerResponse(**response)
    return StatusBannerOrderDict(
        purchase_date=order.data.order.dateAndTime.date,
        delivery_date=order.data.order.deliveryMethods[
            0
        ].deliveryDate.estimatedFrom.date,
    )


def parse_costs_order(response: dict[str, Any]):
    order = CostsResponse(**response)
    costs = order.data.order.costs
    return CostsOrderDict(
        delivery_cost=costs.delivery.value, total_cost=costs.total.value
    )


def get_history_datetime(item: HistoryItem):
    return f"{item.dateAndTime.date}T{item.dateAndTime.time}"


def parse_history(response: dict[str, Any]):
    history = History(**response)
    return [
        PurchaseHistoryItemDict(
            id=i.id,
            status=i.status,
            price=i.totalCost.value or 0,
            datetime=get_history_datetime(i),
            datetime_formatted=i.dateAndTime.formattedLongDateTime,
            store=translate(STORE_NAMES, i.storeName),
        )
        for i in history.data.history
    ]
