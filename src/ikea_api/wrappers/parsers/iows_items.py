import json
import re
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel

from ikea_api.constants import Constants
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.item_base import (
    ItemCode,
    ItemType,
    get_is_combination_from_item_type,
)


class CatalogElement(BaseModel):
    CatalogElementName: Union[str, Dict[Any, Any]]
    CatalogElementId: Union[int, str, Dict[Any, Any]]


class CatalogElementList(BaseModel):
    CatalogElement: Union[CatalogElement, List[CatalogElement]]


class Catalog(BaseModel):
    CatalogElementList: CatalogElementList


class CatalogRefList(BaseModel):
    CatalogRef: Optional[Union[List[Catalog], Catalog]]


class Image(BaseModel):
    ImageUrl: Union[str, Dict[Any, Any]]
    ImageType: str
    ImageSize: str


class RetailItemImageList(BaseModel):
    RetailItemImage: List[Image]


class Measurement(BaseModel):
    PackageMeasureType: str
    PackageMeasureTextMetric: str


class RetailItemCommPackageMeasureList(BaseModel):
    RetailItemCommPackageMeasure: List[Measurement]


class GenericItem(BaseModel):
    ItemNo: ItemCode
    ProductName: str
    ProductTypeName: str


class ChildItem(GenericItem):
    Quantity: int
    # For `get_name`
    ItemMeasureReferenceTextMetric: None = None
    ValidDesignText: None = None
    RetailItemCommPackageMeasureList: Optional[RetailItemCommPackageMeasureList]


class RetailItemCommChildList(BaseModel):
    RetailItemCommChild: Union[List[ChildItem], ChildItem]


class Price(BaseModel):
    Price: int


class RetailItemCommPriceList(BaseModel):
    RetailItemCommPrice: Union[Price, List[Price]]


class ResponseIowsItem(GenericItem):
    ItemType: ItemType
    CatalogRefList: CatalogRefList
    ItemMeasureReferenceTextMetric: Optional[str]
    ValidDesignText: Optional[str]
    RetailItemCommPackageMeasureList: Optional[RetailItemCommPackageMeasureList]
    RetailItemImageList: RetailItemImageList
    RetailItemCommChildList: Optional[RetailItemCommChildList]
    RetailItemCommPriceList: RetailItemCommPriceList


def get_rid_of_dollars(d: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(
        re.sub(
            pattern=r'{"\$": ([^}]+)}',
            repl=lambda x: x.group(1) if x.group(1) else "",
            string=json.dumps(d),
        )
    )


def get_name(item: Union[ChildItem, ResponseIowsItem]) -> str:
    return ", ".join(
        part
        for part in (
            item.ProductName,
            item.ProductTypeName.capitalize(),
            item.ValidDesignText,
            item.ItemMeasureReferenceTextMetric,
        )
        if part
    )


def get_image_url(constants: Constants, images: List[Image]) -> Optional[str]:
    # Filter images first in case no image with S5 size found
    images = [
        i
        for i in images
        if i.ImageType != "LINE DRAWING"
        and isinstance(i.ImageUrl, str)
        and i.ImageUrl.endswith((".png", ".jpg", ".PNG", ".JPG"))
    ]
    if not images:
        return

    for image in images:
        if image.ImageSize == "S5":
            return constants.base_url + cast(str, image.ImageUrl)
    return constants.base_url + cast(str, images[0].ImageUrl)


def parse_weight(v: str) -> float:
    matches = re.findall(r"[0-9.,]+", v)
    if matches:
        return float(matches[0])
    return 0.0


def get_weight(measurements: List[Measurement]) -> float:
    weight = 0.0
    if not measurements:
        return weight

    for m in measurements:
        if m.PackageMeasureType == "WEIGHT":
            weight += parse_weight(m.PackageMeasureTextMetric)
    return weight


def get_child_items(
    child_items: Union[List[ChildItem], ChildItem]
) -> List[types.ChildItem]:
    if not child_items:
        return []
    if isinstance(child_items, ChildItem):
        child_items = [child_items]

    return [
        types.ChildItem(
            name=get_name(child),
            item_code=child.ItemNo,
            weight=get_weight(
                child.RetailItemCommPackageMeasureList.RetailItemCommPackageMeasure
                if child.RetailItemCommPackageMeasureList
                else []
            ),
            qty=child.Quantity,
        )
        for child in child_items
    ]


def get_price(prices: Union[Price, List[Price]]) -> int:
    if not prices:
        return 0
    if isinstance(prices, list):
        return min(p.Price for p in prices)
    return prices.Price


def get_url(constants: Constants, item_code: str, is_combination: bool) -> str:
    suffix = "s" if is_combination else ""
    return f"{constants.local_base_url}/p/-{suffix}{item_code}"


def get_category_name_and_url(
    constants: Constants, catalogs: Optional[Union[List[Catalog], Catalog]]
):
    if not catalogs:
        return None, None
    if isinstance(catalogs, Catalog):
        catalogs = [catalogs]

    idx = 0 if len(catalogs) == 1 else 1
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
        f"{constants.local_base_url}/cat/-{category.CatalogElementId}",
    )


def parse_iows_item(constants: Constants, response: Dict[str, Any]) -> types.ParsedItem:
    response = get_rid_of_dollars(response)
    item = ResponseIowsItem(**response)

    is_combination = get_is_combination_from_item_type(item.ItemType)
    weight = (
        get_weight(item.RetailItemCommPackageMeasureList.RetailItemCommPackageMeasure)
        if item.RetailItemCommPackageMeasureList
        else 0.0
    )
    child_items = (
        item.RetailItemCommChildList.RetailItemCommChild
        if item.RetailItemCommChildList
        else []
    )
    category_name, category_url = get_category_name_and_url(
        constants, item.CatalogRefList.CatalogRef
    )

    return types.ParsedItem(
        is_combination=is_combination,
        item_code=item.ItemNo,
        name=get_name(item),
        image_url=get_image_url(constants, item.RetailItemImageList.RetailItemImage),
        weight=weight,
        child_items=get_child_items(child_items),
        price=get_price(item.RetailItemCommPriceList.RetailItemCommPrice),
        url=get_url(constants, item.ItemNo, is_combination),
        category_name=category_name,
        category_url=category_url,  # type: ignore
    )
