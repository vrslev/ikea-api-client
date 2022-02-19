from __future__ import annotations

import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from ikea_api.constants import Constants
from ikea_api.utils import translate_from_dict
from ikea_api.wrappers import types

STORE_NAMES = {"ru": {"IKEA": "Интернет-магазин", "Санкт-Петербург: Парнас": "Парнас"}}


class DateAndTime(BaseModel):
    date: datetime.date


class DeliveryDate(BaseModel):
    estimatedFrom: DateAndTime


class DeliveryMethod(BaseModel):
    deliveryDate: DeliveryDate


class StatusBannerOrder(BaseModel):
    dateAndTime: DateAndTime
    deliveryMethods: List[DeliveryMethod]


class StatusBannerData(BaseModel):
    order: StatusBannerOrder


class ResponseStatusBanner(BaseModel):
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


class ResponseCosts(BaseModel):
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
    history: List[HistoryItem]


class ResponseHistory(BaseModel):
    data: HistoryData


def parse_status_banner_order(response: dict[str, Any]) -> types.StatusBannerOrder:
    order = ResponseStatusBanner(**response)
    return types.StatusBannerOrder(
        purchase_date=order.data.order.dateAndTime.date,
        delivery_date=order.data.order.deliveryMethods[
            0
        ].deliveryDate.estimatedFrom.date,
    )


def parse_costs_order(response: dict[str, Any]) -> types.CostsOrder:
    order = ResponseCosts(**response)
    costs = order.data.order.costs
    return types.CostsOrder(
        delivery_cost=costs.delivery.value, total_cost=costs.total.value
    )


def get_history_datetime(item: HistoryItem) -> str:
    return f"{item.dateAndTime.date}T{item.dateAndTime.time}"


def parse_history(
    constants: Constants, response: dict[str, Any]
) -> list[types.PurchaseHistoryItem]:
    history = ResponseHistory(**response)
    return [
        types.PurchaseHistoryItem(
            id=i.id,
            status=i.status,
            price=i.totalCost.value or 0,
            datetime=get_history_datetime(i),
            datetime_formatted=i.dateAndTime.formattedLongDateTime,
            store=translate_from_dict(constants, STORE_NAMES, i.storeName),
        )
        for i in history.data.history
    ]
