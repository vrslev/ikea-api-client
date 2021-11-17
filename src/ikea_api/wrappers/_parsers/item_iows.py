import json
import re
from typing import Any, Optional, Union

from pydantic import BaseModel

from ikea_api import Constants
from ikea_api.wrappers._parsers.item_base import (
    ItemCode,
    ItemType,
    get_is_combination_from_item_type,
)
from ikea_api.wrappers.types import ChildItemDict, ParsedItem


class CatalogElement(BaseModel):
    CatalogElementName: Union[str, dict[Any, Any]]
    CatalogElementId: Union[int, str, dict[Any, Any]]


class CatalogElementList(BaseModel):
    CatalogElement: Union[CatalogElement, list[CatalogElement]]


class Catalog(BaseModel):
    CatalogElementList: CatalogElementList


class CatalogRefList(BaseModel):
    CatalogRef: list[Catalog]


class Image(BaseModel):
    ImageUrl: str
    ImageType: str
    ImageSize: str


class RetailItemImageList(BaseModel):
    RetailItemImage: list[Image]


class Measurement(BaseModel):
    PackageMeasureType: str
    PackageMeasureTextMetric: str


class RetailItemCommPackageMeasureList(BaseModel):
    RetailItemCommPackageMeasure: list[Measurement]


class GenericItem(BaseModel):
    ItemNo: ItemCode
    ProductName: str
    ProductTypeName: str


class ChildItem(GenericItem):
    Quantity: int
    # For `get_name`
    ItemMeasureReferenceTextMetric: None = None
    ValidDesignText: None = None
    RetailItemCommPackageMeasureList: RetailItemCommPackageMeasureList


class RetailItemCommChildList(BaseModel):
    RetailItemCommChild: list[ChildItem]


class Price(BaseModel):
    Price: int


class RetailItemCommPriceList(BaseModel):
    RetailItemCommPrice: Union[Price, list[Price]]


class IowsItem(GenericItem):
    ItemType: ItemType
    CatalogRefList: CatalogRefList
    ItemMeasureReferenceTextMetric: str
    ValidDesignText: str
    RetailItemCommPackageMeasureList: Optional[RetailItemCommPackageMeasureList]
    RetailItemImageList: RetailItemImageList
    RetailItemCommChildList: Optional[RetailItemCommChildList]
    RetailItemCommPriceList: RetailItemCommPriceList


def get_rid_of_dollars(d: dict[str, Any]) -> dict[str, Any]:
    dumped = json.dumps(d)
    dumped = re.sub(
        r'{"\$": ([^}]+)}', lambda x: x.group(1) if x.group(1) else "", dumped
    )
    return json.loads(dumped)


def get_name(item: ChildItem | IowsItem):
    return ", ".join(
        part
        for part in (
            item.ProductName,
            item.ProductTypeName.capitalize(),
            item.ItemMeasureReferenceTextMetric,
            item.ValidDesignText,
        )
        if part
    )


def get_image_url(images: list[Image]):
    # Sort images first in case no image with S5 size found
    images = [i for i in images if i.ImageType != "LINE DRAWING"]
    if not images:
        return

    for image in images:
        if not image.ImageUrl.endswith((".png", ".jpg", ".PNG", ".JPG")):
            continue
        if image.ImageSize == "S5":
            return Constants.BASE_URL + image.ImageUrl
    return Constants.BASE_URL + images[0].ImageUrl


def parse_weight(v: str):
    if matches := re.findall(r"[0-9.,]+", v):
        return float(matches[0].replace(",", "."))
    return 0.0


def get_weight(measurements: list[Measurement]):
    weight = 0.0
    if not measurements:
        return weight

    for m in measurements:
        if m.PackageMeasureType == "WEIGHT":
            weight += parse_weight(m.PackageMeasureTextMetric)
    return weight


def get_child_items(child_items: list[ChildItem]) -> list[ChildItemDict]:
    if not child_items:
        return []

    return [
        ChildItemDict(
            item_code=child.ItemNo,
            item_name=get_name(child),
            weight=get_weight(
                child.RetailItemCommPackageMeasureList.RetailItemCommPackageMeasure
            ),
            qty=child.Quantity,
        )
        for child in child_items
    ]


def get_price(prices: Price | list[Price]):
    if not prices:
        return 0
    if isinstance(prices, list):
        return min(p.Price for p in prices)
    return prices.Price


def get_url(item_code: str, is_combination: bool):
    suffix = "s" if is_combination else ""
    return (
        f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/"
        + f"{Constants.LANGUAGE_CODE}/p/-{suffix}{item_code}"
    )


def get_category_name_and_url(catalogs: list[Catalog]):
    idx = 0 if len(catalogs) == 1 else 1  # TODO: Why?
    category = catalogs[idx].CatalogElementList.CatalogElement
    if not category:
        return None, None
    if isinstance(category, list):
        category = category[0]
    if isinstance(category.CatalogElementName, dict) or isinstance(
        category.CatalogElementId, dict
    ):
        return None, None
    return (
        category.CatalogElementName,
        f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/"
        + f"{Constants.LANGUAGE_CODE}/cat/-{category.CatalogElementId}",
    )


def main(response: dict[str, Any]):
    response = get_rid_of_dollars(response)
    # raise Exception(response.keys())
    parsed_response = IowsItem(**response)

    is_combination = get_is_combination_from_item_type(parsed_response.ItemType)
    item_code = parsed_response.ItemNo

    if measure_list_chunk := parsed_response.RetailItemCommPackageMeasureList:
        weight = get_weight(measure_list_chunk.RetailItemCommPackageMeasure)
    else:
        weight = 0.0

    raw_child_items = (
        parsed_response.RetailItemCommChildList.RetailItemCommChild
        if parsed_response.RetailItemCommChildList
        else []
    )
    category_name, category_url = get_category_name_and_url(
        parsed_response.CatalogRefList.CatalogRef
    )

    return ParsedItem(
        is_combination=is_combination,
        item_code=item_code,
        name=get_name(parsed_response),
        image_url=get_image_url(parsed_response.RetailItemImageList.RetailItemImage),
        weight=weight,
        child_items=get_child_items(raw_child_items),
        price=get_price(parsed_response.RetailItemCommPriceList.RetailItemCommPrice),
        url=get_url(item_code, is_combination),
        category_name=category_name,
        category_url=category_url,
    )
