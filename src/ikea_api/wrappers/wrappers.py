# TODO: add tests
from __future__ import annotations

import asyncio
from typing import Any, Optional

from ikea_api.constants import Constants
from ikea_api.endpoints import (
    cart,
    ingka_items,
    iows_items,
    order_capture,
    pip_item,
    purchases,
)
from ikea_api.exceptions import GraphQLError
from ikea_api.executors.httpx import run as run_with_httpx
from ikea_api.executors.requests import run as run_with_requests
from ikea_api.utils import parse_item_codes
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers import purchases as purchases_parser
from ikea_api.wrappers.parsers.ingka_items import main as parse_ingka_items
from ikea_api.wrappers.parsers.iows_items import main as parse_iows_items
from ikea_api.wrappers.parsers.order_capture import main as parse_order_capture
from ikea_api.wrappers.parsers.pip_item import main as parse_pip_item

try:
    from pydantic import BaseModel
except ImportError:
    raise RuntimeError(
        "To use wrappers you need Pydantic to be installed. "
        + "Run 'pip install \"ikea_api[wrappers]\"' to do so."
    )


def get_purchase_history(purchases: purchases.API) -> list[types.PurchaseHistoryItem]:
    response = run_with_requests(purchases.history())
    return purchases_parser.parse_history(purchases.const, response)


def get_purchase_info(
    purchases: purchases.API, *, order_number: str, email: str | None = None
) -> types.PurchaseInfo:
    endpoint = purchases.order_info(
        order_number=order_number,
        email=email,
        queries=["StatusBannerOrder", "CostsOrder"],
    )
    status_banner, costs = run_with_requests(endpoint)
    return types.PurchaseInfo(
        **purchases_parser.parse_status_banner_order(status_banner).dict(),
        **purchases_parser.parse_costs_order(costs).dict(),
    )


class _ExtensionsData(BaseModel):
    itemNos: list[str]


class _Extensions(BaseModel):
    code: str
    data: Optional[_ExtensionsData]


class _CartErrorRef(BaseModel):
    extensions: _Extensions


def add_items_to_cart(cart: cart.API, items: dict[str, int]) -> types.CannotAddItems:
    run_with_requests(cart.clear())
    cannot_add_items: list[str] = []

    while pending_items := items.copy():
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
    cart_ = cart.API(constants, token=token)
    order_capture_ = order_capture.API(constants, token=token)

    cannot_add = add_items_to_cart(cart_, items)
    cannot_add_all_items = not set(items.keys()) ^ set(cannot_add)
    if cannot_add_all_items:
        return types.GetDeliveryServicesResponse(
            delivery_options=[], cannot_add=cannot_add
        )

    cart_response = await run_with_httpx(cart_.show())
    checkout_items = order_capture.convert_cart_to_checkout_items(cart_response)
    checkout_id = await run_with_httpx(order_capture_.get_checkout(checkout_items))
    service_area = await run_with_httpx(
        order_capture_.get_service_area(checkout_id, zip_code=zip_code)
    )

    home, collect = await asyncio.gather(
        run_with_httpx(
            order_capture_.get_home_delivery_services(checkout_id, service_area),
        ),
        run_with_httpx(
            order_capture_.get_collect_delivery_services(checkout_id, service_area)
        ),
    )

    parsed_data = parse_order_capture(
        constants=constants,
        home_delivery_services_response=home,
        collect_delivery_services_response=collect,
    )
    return types.GetDeliveryServicesResponse(
        delivery_options=parsed_data, cannot_add=cannot_add
    )


def _chunks(list_: list[Any], chunk_size: int):
    return (list_[i : i + chunk_size] for i in range(0, len(list_), chunk_size))


async def _get_ingka_items(constants: Constants, item_codes: list[str]):
    api = ingka_items.API(constants)
    tasks = (run_with_httpx(api.get_items(c)) for c in _chunks(item_codes, 50))
    responses = await asyncio.gather(*tasks)

    res: list[types.IngkaItem] = []
    for response in responses:
        res += parse_ingka_items(constants, response)
    return res


async def _get_pip_items(constants: Constants, item_codes: list[str]):
    api = pip_item.API(constants)
    tasks = (run_with_httpx(api.get_item(i)) for i in item_codes)
    responses = await asyncio.gather(*tasks)
    return [parse_pip_item(r) for r in responses]


def _get_pip_items_map(items: list[types.PipItem | None]):
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


async def _get_iows_items(constants: Constants, item_codes: list[str]):
    api = iows_items.API(constants)
    tasks = (run_with_httpx(api.get_items(c)) for c in _chunks(item_codes, 90))
    responses = await asyncio.gather(*tasks)

    res: list[types.ParsedItem] = []
    for items in responses:
        res += (parse_iows_items(constants, i) for i in items)
    return res


async def get_items(
    constants: Constants, item_codes: list[str]
) -> list[types.ParsedItem]:
    pending = parse_item_codes(item_codes, unshorten_ingka_pagelinks=True)
    ingka_pip = await _get_ingka_pip_items(constants=constants, item_codes=pending)

    fetched = {i.item_code for i in ingka_pip}
    pending = [i for i in pending if i not in fetched]
    if not pending:
        return ingka_pip

    iows = await _get_iows_items(constants=constants, item_codes=pending)
    return ingka_pip + iows