from typing import Any

from ikea_api import IkeaApi
from ikea_api._endpoints.item_ingka import IngkaItems
from ikea_api._endpoints.item_iows import IowsItems
from ikea_api._endpoints.item_pip import PipItem
from ikea_api._utils import parse_item_codes
from ikea_api.exceptions import GraphQLError, ItemFetchError, OrderCaptureError
from ikea_api.wrappers._parsers.item_ingka import main as parse_ingka_item
from ikea_api.wrappers._parsers.item_iows import main as parse_iows_item
from ikea_api.wrappers._parsers.item_pip import main as parse_pip_item
from ikea_api.wrappers._parsers.order_capture import main as parse_delivery_options
from ikea_api.wrappers._parsers.purchases import CostsOrder, StatusBannerOrder
from ikea_api.wrappers._parsers.purchases import parse_history as parse_purchase_history
from ikea_api.wrappers.types import (
    AddItemsToCartResponse,
    GetDeliveryServicesResponse,
    IngkaItemDict,
    ParsedItem,
    PipItemDict,
    PurchaseHistoryItemDict,
    PurchaseInfoDict,
)


class NoDeliveryOptionsAvailableError(OrderCaptureError):
    pass


def get_purchase_history(api: IkeaApi) -> list[PurchaseHistoryItemDict]:
    response = api.purchases.history()
    return parse_purchase_history(response)  # type: ignore


def get_purchase_info(
    api: IkeaApi, purchase_id: str, email: str | None = None
) -> PurchaseInfoDict:
    status_banner, costs = api.purchases.order_info(
        purchase_id,
        email=email,
        queries=["StatusBannerOrder", "CostsOrder"],
    )
    res: PurchaseInfoDict = StatusBannerOrder(status_banner)() | CostsOrder(costs)()  # type: ignore
    if not any(res.values()):
        return {}  # type: ignore
    return res


def get_delivery_services(
    api: IkeaApi, items: dict[str, int], zip_code: str
) -> GetDeliveryServicesResponse:
    cannot_add = add_items_to_cart(api, items)["cannot_add"]
    if not set(items.keys()) ^ set(cannot_add):  # if cannot add all items
        return GetDeliveryServicesResponse(delivery_options=[], cannot_add=cannot_add)

    try:
        response = api.order_capture(zip_code)
    except OrderCaptureError as e:
        if e.error_code in [60005, 60006]:
            raise NoDeliveryOptionsAvailableError
        else:
            raise

    options = parse_delivery_options(response)  # type: ignore
    return GetDeliveryServicesResponse(delivery_options=options, cannot_add=cannot_add)


def add_items_to_cart(api: IkeaApi, items: dict[str, int]) -> AddItemsToCartResponse:
    api.cart.clear()

    res = AddItemsToCartResponse(cannot_add=[], message=None)
    items_to_add = items.copy()

    while True:
        try:
            res["message"] = api.cart.add_items(items_to_add)  # type: ignore
            break
        except GraphQLError as exc:
            if not res["cannot_add"]:
                res["cannot_add"] = []

            if exc.errors is None:
                raise

            for error in exc.errors:
                if error["extensions"]["code"] == "INVALID_ITEM_NUMBER":
                    res["cannot_add"] += error["extensions"]["data"]["itemNos"]
                else:
                    raise

            for item in res["cannot_add"]:
                items_to_add.pop(item)

            if not items_to_add:
                break
    return res


def _get_iows_items(item_codes: list[str]):
    fetched: list[Any] = []
    try:
        fetched = IowsItems()(item_codes)
    except ItemFetchError as e:
        if not "Wrong Item Code" in e.args[0]:
            raise
    return [parse_iows_item(item) for item in fetched]


def _bind_ingka_and_pip_objects(ingka: IngkaItemDict, pip: PipItemDict) -> ParsedItem:
    return ingka | pip  # type: ignore


def _get_ingka_pip_items(item_codes: list[str]):
    res: list[ParsedItem] = []
    items_ingka: list[IngkaItemDict] = []
    items_to_fetch_pip: dict[str, bool] = {}

    for chunk in IngkaItems()(item_codes):
        for fetched_item in chunk["data"]:
            parsed_item = parse_ingka_item(fetched_item)
            items_ingka.append(parsed_item)
            items_to_fetch_pip[parsed_item["item_code"]] = parsed_item["is_combination"]

    fetched_items_map_pip: dict[str, PipItemDict] = {}
    pip_item_fetcher = PipItem()
    for item_code in items_to_fetch_pip:
        fetched_item = pip_item_fetcher(item_code)
        parsed_item = parse_pip_item(fetched_item)
        fetched_items_map_pip[parsed_item["item_code"]] = parsed_item

    for item_ingka in items_ingka:
        item_pip: PipItemDict | None = fetched_items_map_pip.get(
            item_ingka["item_code"]
        )
        if item_pip is None:
            continue

        parsed_item = _bind_ingka_and_pip_objects(item_ingka, item_pip)
        res.append(parsed_item)

    return res


def get_items(item_codes: list[str]) -> list[ParsedItem]:
    items_to_fetch = parse_item_codes(item_codes)
    fetched_items: list[ParsedItem] = []

    def update_items_to_fetch():
        nonlocal items_to_fetch
        items_to_fetch = [
            item
            for item in items_to_fetch
            if item not in (i["item_code"] for i in fetched_items)
        ]

    fetched_items += _get_iows_items(items_to_fetch)
    update_items_to_fetch()

    if not items_to_fetch:
        return fetched_items

    fetched_items += _get_ingka_pip_items(items_to_fetch)

    return fetched_items
