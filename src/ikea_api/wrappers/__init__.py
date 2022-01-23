from __future__ import annotations

from typing import Any, List, Optional

try:
    from pydantic import BaseModel
except ImportError:
    raise RuntimeError(
        "To use wrappers you need Pydantic to be installed. "
        + "Run 'pip install \"ikea_api[wrappers]\"' to do so."
    )

from ikea_api import IKEA
from ikea_api._endpoints.item_ingka import IngkaItems
from ikea_api._endpoints.item_iows import IowsItems
from ikea_api._endpoints.item_pip import PipItem
from ikea_api._utils import parse_item_codes
from ikea_api.exceptions import GraphQLError, ItemFetchError
from ikea_api.wrappers import types
from ikea_api.wrappers._parsers import (
    item_ingka,
    item_iows,
    item_pip,
    order_capture,
    purchases,
)

__all__ = [
    "get_purchase_history",
    "get_purchase_info",
    "add_items_to_cart",
    "get_delivery_services",
    "get_items",
]


def get_purchase_history(api: IKEA) -> list[types.PurchaseHistoryItem]:
    response = api.purchases.history()
    return purchases.parse_history(response)


def get_purchase_info(
    api: IKEA, *, id: str, email: str | None = None
) -> types.PurchaseInfo:
    status_banner_resp, costs_resp = api.purchases.order_info(
        order_number=id, email=email, queries=["StatusBannerOrder", "CostsOrder"]
    )

    status_banner = purchases.parse_status_banner_order(status_banner_resp)
    costs = purchases.parse_costs_order(costs_resp)
    return types.PurchaseInfo(**status_banner.dict(), **costs.dict())


class _CartErrorExtensionsData(BaseModel):
    itemNos: List[str]


class _CartErrorExtensions(BaseModel):
    code: str
    data: Optional[_CartErrorExtensionsData]


class _CartError(BaseModel):
    extensions: _CartErrorExtensions


def add_items_to_cart(api: IKEA, *, items: dict[str, int]) -> types.CannotAddItems:
    api.cart.clear()
    pending_items = items.copy()
    cannot_add_items: list[str] = []

    while pending_items:
        try:
            api.cart.add_items(pending_items)
            break
        except GraphQLError as exc:
            errors: list[dict[str, Any]] = exc.errors  # type: ignore
            for error_dict in errors:
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
    api: IKEA, *, items: dict[str, int], zip_code: str
) -> types.GetDeliveryServicesResponse:
    cannot_add = add_items_to_cart(api, items=items)
    cannot_add_all_items = not set(items.keys()) ^ set(cannot_add)
    if cannot_add_all_items:
        return types.GetDeliveryServicesResponse(
            delivery_options=[], cannot_add=cannot_add
        )

    order_capture_api = api.order_capture(zip_code=zip_code)
    checkout = order_capture_api._get_checkout(
        order_capture_api._get_items_for_checkout()
    )
    service_area = order_capture_api._get_service_area(checkout)
    home_response = order_capture_api.get_home_delivery_services(
        (checkout, service_area)
    )
    collect_response = order_capture_api.get_collect_delivery_services(
        (checkout, service_area)
    )
    parsed_responses = order_capture.main(
        home_delivery_services_response=home_response,
        collect_delivery_services_response=collect_response,
    )
    return types.GetDeliveryServicesResponse(
        delivery_options=parsed_responses, cannot_add=cannot_add
    )


def _split_to_chunks(list_: list[Any], chunk_size: int):
    return (list_[i : i + chunk_size] for i in range(0, len(list_), chunk_size))


def _get_iows_items(item_codes: list[str]):
    responses: list[Any] = []
    fetcher = IowsItems()
    for item_codes_chunk in _split_to_chunks(item_codes, 90):
        try:
            responses += fetcher(item_codes_chunk)
        except ItemFetchError as exc:
            if "Wrong Item Code" not in exc.args[0]:
                raise
    return [item_iows.main(r) for r in responses]


def _get_ingka_items(item_codes: list[str]):
    responses: list[Any] = []
    fetcher = IngkaItems()
    for item_codes_chunk in _split_to_chunks(item_codes, 50):
        responses.append(fetcher(item_codes_chunk))
    res: list[types.IngkaItem] = []
    for resp in responses:
        res += item_ingka.main(resp)
    return res


def _get_pip_items(item_codes: list[str]):
    fetcher = PipItem()
    responses = (fetcher(i) for i in item_codes)
    return [item_pip.main(r) for r in responses]


def _get_pip_items_map(items: list[types.PipItem | None]):
    res: dict[str, types.PipItem] = {}
    for item in items:
        if item:
            res[item.item_code] = item
    return res


def _get_ingka_pip_items(item_codes: list[str]) -> list[types.ParsedItem]:
    ingka_items = _get_ingka_items(item_codes)
    pip_items = _get_pip_items(item_codes)
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


def get_items(item_codes: list[str]) -> list[types.ParsedItem]:
    pending_item_codes = parse_item_codes(item_codes, unshorten_ingka_pagelinks=True)
    fetched_items_ingka_pip = _get_ingka_pip_items(pending_item_codes)

    fetched_item_codes = [i.item_code for i in fetched_items_ingka_pip]
    pending_item_codes = [i for i in pending_item_codes if i not in fetched_item_codes]
    if not pending_item_codes:
        return fetched_items_ingka_pip

    fetched_items_iows = _get_iows_items(pending_item_codes)
    return fetched_items_ingka_pip + fetched_items_iows
