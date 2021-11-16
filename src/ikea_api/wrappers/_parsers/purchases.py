from __future__ import annotations

from typing import Any

from box import Box

from ikea_api.wrappers._parsers import get_box
from ikea_api.wrappers.types import (
    CostsOrderDict,
    PurchaseHistoryItemDict,
    StatusBannerOrderDict,
)

STORE_NAMES = {"IKEA": "Интернет-магазин", "Санкт-Петербург: Парнас": "Парнас"}

# pyright: reportUnknownMemberType=false


def parse_purchase_history(history: dict[str, Any]) -> list[PurchaseHistoryItemDict]:
    list_: list[Box] = get_box(history).data.history
    return [PurchaseHistoryItem(i)() for i in list_]


class PurchaseHistoryItem:
    def __init__(self, history_item: Box):
        self.d = history_item

    def get_datetime(self):
        if self.d.dateAndTime.date and self.d.dateAndTime.time:
            return f"{self.d.dateAndTime.date}T{self.d.dateAndTime.time}"

    def get_datetime_formatted(self):
        datetime_fmt: str = self.d.dateAndTime.formattedLongDateTime
        return datetime_fmt

    def get_price(self):
        price: float | None = self.d.totalCost.value
        return price or 0.0

    def get_purchase_id(self):
        purchase_id: int = self.d.id
        return purchase_id

    def get_status(self):
        status: str = self.d.status
        return status

    def get_store(self):
        store_name: str = self.d.storeName
        return STORE_NAMES.get(store_name)

    def __call__(self) -> PurchaseHistoryItemDict:
        return PurchaseHistoryItemDict(
            datetime=self.get_datetime(),
            datetime_formatted=self.get_datetime_formatted(),
            price=self.get_price(),
            purchase_id=self.get_purchase_id(),
            status=self.get_status(),
            store=self.get_store(),
        )


class CostsOrder:
    def __init__(self, costs_order: dict[str, Any]):
        self.d = get_box(costs_order).data.order.costs

    def get_delivery_cost(self):
        delivery_cost: float | None = self.d.delivery.value
        return delivery_cost or 0.0

    def get_total_cost(self):
        total_cost: float | None = self.d.total.value
        return total_cost or 0.0

    def __call__(self):
        return CostsOrderDict(
            delivery_cost=self.get_delivery_cost(),
            total_cost=self.get_total_cost(),
        )


class StatusBannerOrder:
    def __init__(self, status_banner_order: dict[str, Any]):
        self.d = get_box(status_banner_order).data.order

    def get_purchase_date(self):
        purchase_date: str | None = self.d.dateAndTime.date
        return purchase_date

    def get_delivery_date(self):
        delivery_methods: list[Box] = self.d.deliveryMethods
        if delivery_methods:
            delivery_date: str | None = delivery_methods[
                0
            ].deliveryDate.estimatedFrom.date
            return delivery_date

    def __call__(self):
        return StatusBannerOrderDict(
            purchase_date=self.get_purchase_date(),
            delivery_date=self.get_delivery_date(),
        )
