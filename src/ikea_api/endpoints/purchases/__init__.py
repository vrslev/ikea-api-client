from __future__ import annotations

from enum import Enum
from typing import Any

from ikea_api.api import API
from ikea_api.constants import Constants

from . import queries as _queries


class OrderInfoQuery(Enum):
    StatusBannerOrder = "StatusBannerOrder"
    CostsOrder = "CostsOrder"
    ProductListOrder = "ProductListOrder"


class Purchases(API):
    def __init__(self, token: str):
        super().__init__(token, "https://purchase-history.ocp.ingka.ikea.com/graphql")
        origin = "https://order.ikea.com"
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": Constants.LANGUAGE_CODE
                + "-"
                + Constants.COUNTRY_CODE,
                "Origin": origin,
                "Referer": f"{origin}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/purchases/",
            }
        )

    def _build_payload(
        self, operation_name: str | OrderInfoQuery, query: str, **variables: Any
    ):
        payload: dict[str, Any] = {
            "operationName": operation_name,
            "variables": {**variables},
            "query": query,
        }
        return payload

    def history(self, take: int = 5, skip: int = 0):
        """
        Get purchase history.

        Parameters are for pagination.
        If you want to see all your purchases set 'take' to 10000
        """
        payload = self._build_payload("History", _queries.history, take=take, skip=skip)
        return self._call_api(data=payload)

    def order_info(
        self,
        order_number: str | int,
        email: str | None = None,
        queries: list[OrderInfoQuery] = [
            OrderInfoQuery.StatusBannerOrder,
            OrderInfoQuery.CostsOrder,
            OrderInfoQuery.ProductListOrder,
        ],
        skip_products: int = 0,
        skip_product_prices: bool = False,
        take_products: int = 10,
    ):
        """
        Get order information: status and costs.

        :params order_number: ID of your purchase
        :params email: Your email. If set, there's no need to get token.
        :params queries: which queries to include in request
        :params skip_products: Relevant to ProductListOrder
        :params skip_product_prices: Relevant to ProductListOrder
        :params take_products: Relevant to ProductListOrder
        """
        order_number = str(order_number)
        headers = {"Referer": f"{self._session.headers['Origin']}/{order_number}/"}

        payload: list[dict[str, dict[str, Any]]] = []
        if OrderInfoQuery.StatusBannerOrder in queries:
            payload.append(
                self._build_payload(
                    "StatusBannerOrder",
                    _queries.status_banner_order,
                    orderNumber=order_number,
                )
            )
        if OrderInfoQuery.CostsOrder in queries:
            payload.append(
                self._build_payload(
                    "CostsOrder",
                    _queries.costs_order,
                    orderNumber=order_number,
                )
            )
        if OrderInfoQuery.ProductListOrder in queries:
            payload.append(
                self._build_payload(
                    "ProductListOrder",
                    _queries.product_list_order,
                    orderNumber=order_number,
                    receiptNumber="",
                    skip=skip_products,
                    skipPrice=skip_product_prices,
                    take=take_products,
                )
            )

        if email:
            headers["Referer"] = self._session.headers["Referer"] + "lookup"
            for d in payload:
                d["variables"]["liteId"] = email

        return self._call_api(headers=headers, data=payload)
