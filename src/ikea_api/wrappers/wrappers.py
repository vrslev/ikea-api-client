from __future__ import annotations

import asyncio
from typing import Any, Iterable, List, Optional, cast

from pydantic import BaseModel

from ikea_api.constants import Constants
from ikea_api.endpoints.cart import Cart
from ikea_api.endpoints.ingka_items import IngkaItems
from ikea_api.endpoints.iows_items import IowsItems
from ikea_api.endpoints.order_capture import (
    OrderCapture,
    convert_cart_to_checkout_items,
)
from ikea_api.endpoints.pip_item import PipItem
from ikea_api.endpoints.purchases import Purchases
from ikea_api.exceptions import GraphQLError
from ikea_api.executors.httpx import run_async as run_with_httpx
from ikea_api.executors.requests import run as run_with_requests
from ikea_api.utils import parse_item_codes, unshorten_urls_from_ingka_pagelinks
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.ingka_items import parse_ingka_items
from ikea_api.wrappers.parsers.iows_items import parse_iows_item
from ikea_api.wrappers.parsers.order_capture import parse_delivery_services
from ikea_api.wrappers.parsers.pip_item import parse_pip_item
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
        **parse_status_banner_order(status_banner).dict(),
        **parse_costs_order(costs).dict(),
    )


class _ExtensionsData(BaseModel):
    itemNos: List[str]


class _Extensions(BaseModel):
    code: str
    data: Optional[_ExtensionsData]


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
                error = _CartErrorRef(**error_dict)
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


def chunks(list_: list[Any], chunk_size: int) -> Iterable[list[Any]]:
    return (list_[i : i + chunk_size] for i in range(0, len(list_), chunk_size))


async def _get_ingka_items(
    constants: Constants, item_codes: list[str]
) -> list[types.IngkaItem]:
    api = IngkaItems(constants)
    tasks = (run_with_httpx(api.get_items(c)) for c in chunks(item_codes, 50))
    responses = await asyncio.gather(*tasks)
    res: list[types.IngkaItem] = []
    for response in responses:
        res += parse_ingka_items(constants, response)
    return res


async def _get_pip_items(
    constants: Constants, item_codes: list[str]
) -> list[types.PipItem | None]:
    api = PipItem(constants)
    tasks = (run_with_httpx(api.get_item(i)) for i in item_codes)
    responses = await asyncio.gather(*tasks)
    return [parse_pip_item(r) for r in responses]


def _get_pip_items_map(items: list[types.PipItem | None]) -> dict[str, types.PipItem]:
    res: dict[str, types.PipItem] = {}
    for item in items:
        if item:
            res[item.item_code] = item
    return res


async def _get_ingka_pip_items(
    constants: Constants, item_codes: list[str]
) -> list[types.ParsedItem]:
    ingka_resp, pip_resp = await asyncio.gather(
        _get_ingka_items(constants=constants, item_codes=item_codes),
        _get_pip_items(constants=constants, item_codes=item_codes),
    )
    pip_items_map = _get_pip_items_map(pip_resp)

    res: list[types.ParsedItem] = []
    for ingka_item in ingka_resp:
        pip_item_ = pip_items_map.get(ingka_item.item_code)
        if pip_item_ is None:
            continue
        item = types.ParsedItem(
            is_combination=ingka_item.is_combination,
            item_code=ingka_item.item_code,
            name=ingka_item.name,
            image_url=ingka_item.image_url,
            weight=ingka_item.weight,
            child_items=ingka_item.child_items,
            price=pip_item_.price,
            url=pip_item_.url,
            category_name=pip_item_.category_name,
            category_url=pip_item_.category_url,
        )
        res.append(item)
    return res


async def _get_iows_items(
    constants: Constants, item_codes: list[str]
) -> list[types.ParsedItem]:
    api = IowsItems(constants)
    tasks = (run_with_httpx(api.get_items(c)) for c in chunks(item_codes, 90))
    responses = cast("tuple[list[dict[str, Any]], ...]", await asyncio.gather(*tasks))

    res: list[types.ParsedItem] = []
    for items in responses:
        res += (parse_iows_item(constants, i) for i in items)
    return res


async def get_items(
    constants: Constants, item_codes: list[str]
) -> list[types.ParsedItem]:
    item_codes_ = item_codes.copy()
    item_codes_ += await unshorten_urls_from_ingka_pagelinks(
        str(item_codes)
    )  # TODO: Don't do this
    pending = parse_item_codes(item_codes_)
    ingka_pip = await _get_ingka_pip_items(constants=constants, item_codes=pending)

    fetched = {i.item_code for i in ingka_pip}
    pending = [i for i in pending if i not in fetched]
    if not pending:
        return ingka_pip

    iows = await _get_iows_items(constants=constants, item_codes=pending)
    return ingka_pip + iows
