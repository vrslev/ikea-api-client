from __future__ import annotations

import asyncio
from typing import List, Optional

from pydantic import BaseModel

from ikea_api.constants import Constants
from ikea_api.endpoints.cart import Cart
from ikea_api.endpoints.order_capture import (
    OrderCapture,
    convert_cart_to_checkout_items,
)
from ikea_api.endpoints.purchases import Purchases
from ikea_api.exceptions import GraphQLError
from ikea_api.executors.httpx import run_async as run_with_httpx
from ikea_api.executors.requests import run as run_with_requests
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.order_capture import parse_delivery_services
from ikea_api.wrappers.parsers.purchases import (
    parse_costs_order,
    parse_history,
    parse_status_banner_order,
)


def get_purchase_history(purchases: Purchases) -> list[types.PurchaseHistoryItem]:
    response = run_with_requests(purchases.history())
    return parse_history(purchases._const, response)


def get_purchase_info(
    purchases: Purchases, *, order_number: str, email: str | None = None
) -> types.PurchaseInfo:
    endpoint = purchases.order_info(
        order_number=order_number,
        email=email,
        queries=["StatusBannerOrder", "CostsOrder"],
    )
    status_banner, costs = run_with_requests(endpoint)
    return types.PurchaseInfo(
        **parse_status_banner_order(status_banner).model_dump(),
        **parse_costs_order(costs).model_dump(),
    )


class _ExtensionsData(BaseModel):
    itemNos: List[str]


class _Extensions(BaseModel):
    code: str
    data: Optional[_ExtensionsData] = None


class _CartErrorRef(BaseModel):
    extensions: _Extensions


def add_items_to_cart(cart: Cart, items: dict[str, int]) -> types.CannotAddItems:
    run_with_requests(cart.clear())
    cannot_add_items: list[str] = []
    pending_items = items.copy()

    while pending_items:
        try:
            run_with_requests(cart.add_items(pending_items))
            break
        except GraphQLError as exc:
            for error_dict in exc.errors:
                error = _CartErrorRef.model_validate(error_dict)
                if error.extensions.code != "INVALID_ITEM_NUMBER":
                    continue
                if not error.extensions.data:
                    continue
                cannot_add_items += error.extensions.data.itemNos

            for item_code in cannot_add_items:
                pending_items.pop(item_code, None)

    return cannot_add_items


async def get_delivery_services(
    constants: Constants,
    token: str,
    items: dict[str, int],
    zip_code: str,
) -> types.GetDeliveryServicesResponse:
    cart = Cart(constants, token=token)
    order_capture = OrderCapture(constants, token=token)

    cannot_add = add_items_to_cart(cart, items)
    cannot_add_all_items = not set(items.keys()) ^ set(cannot_add)
    if cannot_add_all_items:
        return types.GetDeliveryServicesResponse(
            delivery_options=[], cannot_add=cannot_add
        )

    cart_response = await run_with_httpx(cart.show())
    checkout_items = convert_cart_to_checkout_items(cart_response)
    checkout_id = await run_with_httpx(order_capture.get_checkout(checkout_items))
    service_area_id = await run_with_httpx(
        order_capture.get_service_area(checkout_id, zip_code=zip_code)
    )

    home, collect = await asyncio.gather(
        run_with_httpx(
            order_capture.get_home_delivery_services(checkout_id, service_area_id),
        ),
        run_with_httpx(
            order_capture.get_collect_delivery_services(checkout_id, service_area_id)
        ),
    )

    parsed_data = parse_delivery_services(
        constants=constants,
        home_response=home,
        collect_response=collect,
    )
    return types.GetDeliveryServicesResponse(
        delivery_options=parsed_data, cannot_add=cannot_add
    )
