"""IOWS Item API. Works only for Russian market"""

from __future__ import annotations

from requests import Session

from ikea_api.constants import Constants, Secrets
from ikea_api.errors import ItemFetchError

from . import generic_item_fetcher

# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false


def _build_url(items: dict[str, str]):
    endpoint = "https://iows.ikea.com/retail/iows/ru/ru/catalog/items/"
    templated_list: list[str] = []
    for item in items:
        templated_list.append(f"{items[item]},{item}")
    return endpoint + ";".join(templated_list)


def _fetch_items_specs(session: Session, input_items: list[str]):
    if len(input_items) == 0:
        return
    items: dict[str, str] = {}
    for item in input_items:
        items[item] = "ART"

    for i in range(3):
        url = _build_url(items)
        response = session.get(url)
        if i == 0 and len(items) == 1 and not response.ok:
            items[item] = "SPR"  # type: ignore
            url = _build_url(items)
            response = session.get(url)
            if not response.ok:  # TODO: Bad move
                raise ItemFetchError("Wrong Item Code")

        if not response.text:
            raise ItemFetchError("Wrong Item Code")
        r_json = response.json()

        if "RetailItemCommList" in r_json:
            if "RetailItemComm" in r_json["RetailItemCommList"]:
                return r_json["RetailItemCommList"]["RetailItemComm"]
            else:
                raise ItemFetchError(r_json)

        elif "RetailItemComm" in r_json:
            return [r_json["RetailItemComm"]]

        elif "ErrorList" in r_json:
            errors = r_json["ErrorList"]["Error"]
            if not isinstance(errors, list):
                errors = [errors]

            for err in errors:
                for test in [
                    "ErrorCode" in err,
                    err["ErrorCode"]["$"] == 1101,
                    "ErrorMessage" in err,
                    "ErrorAttributeList" in err,
                    "ErrorAttribute" in err["ErrorAttributeList"],
                ]:
                    if not test:
                        raise ItemFetchError(err)

                attrs = {}
                for attr in err["ErrorAttributeList"]["ErrorAttribute"]:
                    attrs[attr["Name"]["$"]] = attr["Value"]["$"]
                item_code = str(attrs["ITEM_NO"])
                item_type: str = attrs["ITEM_TYPE"]

                if i == 0:
                    items[item_code] = "SPR" if item_type == "ART" else "ART"
                elif i == 1:
                    items.pop(item_code)


def fetch(items: str | list[str]):
    headers = {
        "Accept": "application/vnd.ikea.iows+json;version=2.0",
        "Referer": f"{Constants.BASE_URL}/ru/ru/shoppinglist/",
        "Cache-Control": "no-cache, no-store",  # TODO: Does this required?
        "consumer": Secrets.item_iows_consumer,
        "contract": Secrets.item_iows_contract,
    }
    return generic_item_fetcher(items, headers, _fetch_items_specs, 90)
