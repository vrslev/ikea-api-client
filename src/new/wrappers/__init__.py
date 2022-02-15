from __future__ import annotations

from typing import Any, List, Optional

from new.constants import Constants

try:
    from pydantic import BaseModel
except ImportError:
    raise RuntimeError(
        "To use wrappers you need Pydantic to be installed. "
        + "Run 'pip install \"ikea_api[wrappers]\"' to do so."
    )

from new.endpoints import (
    cart,
    ingka_items,
    iows_items,
    order_capture,
    pip_item,
    purchases,
)
from new.exceptions import GraphQLError, ItemFetchError
from new.executors.requests import execute as run
from new.utils import parse_item_codes
from new.wrappers import parsers, types

__all__ = [
    "get_purchase_history",
    "get_purchase_info",
    "add_items_to_cart",
    "get_delivery_services",
    "get_items",
]


def get_purchase_history(
    constants: Constants, token: str
) -> list[types.PurchaseHistoryItem]:
    response = run(purchases.API(constants, token=token).history())
    return parsers.purchases.parse_history(constants, response)


def get_purchase_info(
    constants: Constants, token: str, *, id: str, email: str | None = None
) -> types.PurchaseInfo:
    gen = purchases.API(constants, token=token).order_info(
        order_number=id, email=email, queries=["StatusBannerOrder", "CostsOrder"]
    )
    status_banner_resp, costs_resp = run(gen)

    status_banner = parsers.purchases.parse_status_banner_order(status_banner_resp)
    costs = parsers.purchases.parse_costs_order(costs_resp)
    return types.PurchaseInfo(**status_banner.dict(), **costs.dict())


class _CartErrorExtensionsData(BaseModel):
    itemNos: List[str]


class _CartErrorExtensions(BaseModel):
    code: str
    data: Optional[_CartErrorExtensionsData]


class _CartError(BaseModel):
    extensions: _CartErrorExtensions


def add_items_to_cart(cart: cart.API, items: dict[str, int]) -> types.CannotAddItems:
    run(cart.clear())

    pending_items = items.copy()
    cannot_add_items: list[str] = []

    while pending_items:
        try:
            run(cart.add_items(pending_items))
            break
        except GraphQLError as exc:
            for error_dict in exc.errors:
                error = _CartError(**error_dict)
                if error.extensions.code != "INVALID_ITEM_NUMBER":
                    continue
                if not error.extensions.data:
                    continue
                cannot_add_items += error.extensions.data.itemNos

            for item_code in cannot_add_items:
                pending_items.pop(item_code, None)

    return cannot_add_items


def get_delivery_services(
    constants: Constants,
    token: str,
    *,
    items: dict[str, int],
    zip_code: str,
) -> types.GetDeliveryServicesResponse:
    cart_ = cart.API(constants, token=token)
    cannot_add = add_items_to_cart(cart_, items)
    cannot_add_all_items = not set(items.keys()) ^ set(cannot_add)
    if cannot_add_all_items:
        return types.GetDeliveryServicesResponse(
            delivery_options=[], cannot_add=cannot_add
        )

    order_capture_ = order_capture.API(constants=constants, token=token)
    cart_response = run(cart_.show())
    checkout_items = order_capture.convert_cart_to_checkout_items(cart_response)
    checkout_id = run(order_capture_.get_checkout(checkout_items))
    service_area = run(order_capture_.get_service_area(checkout_id, zip_code=zip_code))

    home = order_capture_.get_home_delivery_services(  # TODO: Httpx
        checkout_id, service_area
    )
    collect = order_capture_.get_collect_delivery_services(checkout_id, service_area)

    parsed_data = parsers.order_capture.main(
        constants=constants,
        home_delivery_services_response=run(home),
        collect_delivery_services_response=run(collect),
    )

    return types.GetDeliveryServicesResponse(
        delivery_options=parsed_data, cannot_add=cannot_add
    )


def _split_to_chunks(list_: list[Any], chunk_size: int):
    return (list_[i : i + chunk_size] for i in range(0, len(list_), chunk_size))


def _get_iows_items(constants: Constants, item_codes: list[str]):
    responses: list[Any] = []
    fetcher = iows_items.API(constants)
    for item_codes_chunk in _split_to_chunks(item_codes, 90):  # TODO: Httpx
        try:
            responses += run(fetcher.get_items(item_codes_chunk))
        except ItemFetchError as exc:
            if "Wrong Item Code" not in exc.args[0]:
                raise
    return [parsers.item_iows.main(constants=constants, response=r) for r in responses]


def _get_ingka_items(constants: Constants, item_codes: list[str]):
    responses: list[Any] = []
    fetcher = ingka_items.API(constants)
    for item_codes_chunk in _split_to_chunks(item_codes, 50):  # TODO: Httpx
        responses.append(fetcher.get_items(item_codes_chunk))
    res: list[types.IngkaItem] = []
    for resp in responses:
        res += parsers.item_ingka.main(constants=constants, response=resp)
    return res


def _get_pip_items(constants: Constants, item_codes: list[str]):
    fetcher = pip_item.API(constants)
    responses = (run(fetcher.get_item(i)) for i in item_codes)  # TODO: Httpx
    return [parsers.item_pip.main(r) for r in responses]


def _get_pip_items_map(items: list[types.PipItem | None]):
    res: dict[str, types.PipItem] = {}
    for item in items:
        if item:
            res[item.item_code] = item
    return res


def _get_ingka_pip_items(
    constants: Constants, item_codes: list[str]
) -> list[types.ParsedItem]:
    ingka_items = _get_ingka_items(constants=constants, item_codes=item_codes)
    pip_items = _get_pip_items(constants=constants, item_codes=item_codes)
    pip_items_map = _get_pip_items_map(pip_items)

    res: list[types.ParsedItem] = []
    for ingka_item in ingka_items:
        pip_item = pip_items_map.get(ingka_item.item_code)
        if pip_item is None:
            continue
        res.append(
            types.ParsedItem(
                is_combination=ingka_item.is_combination,
                item_code=ingka_item.item_code,
                name=ingka_item.name,
                image_url=ingka_item.image_url,
                weight=ingka_item.weight,
                child_items=ingka_item.child_items,
                price=pip_item.price,
                url=pip_item.url,
                category_name=pip_item.category_name,
                category_url=pip_item.category_url,
            )
        )
    return res


def get_items(constants: Constants, item_codes: list[str]) -> list[types.ParsedItem]:
    pending_item_codes = parse_item_codes(item_codes, unshorten_ingka_pagelinks=True)
    fetched_items_ingka_pip = _get_ingka_pip_items(
        constants=constants, item_codes=pending_item_codes
    )

    fetched_item_codes = [i.item_code for i in fetched_items_ingka_pip]
    pending_item_codes = [i for i in pending_item_codes if i not in fetched_item_codes]
    if not pending_item_codes:
        return fetched_items_ingka_pip

    fetched_items_iows = _get_iows_items(
        constants=constants, item_codes=pending_item_codes
    )
    return fetched_items_ingka_pip + fetched_items_iows
