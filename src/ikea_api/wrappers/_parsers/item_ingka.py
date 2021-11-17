import re
from typing import Any, Optional

from pydantic import BaseModel

from ikea_api._constants import Constants
from ikea_api.exceptions import ParsingError
from ikea_api.wrappers._parsers.item_base import (
    ItemCode,
    ItemType,
    get_is_combination_from_item_type,
)
from ikea_api.wrappers.types import ChildItemDict, IngkaItemDict


class _ItemKey(BaseModel):
    itemType: ItemType
    itemNo: ItemCode


class _PackageMeasurement(BaseModel):
    type: str
    valueMetric: float


class _MediaVariant(BaseModel):
    quality: str
    href: str


class _Media(BaseModel):
    typeName: str
    variants: list[_MediaVariant]


class _ProductType(BaseModel):
    name: str


class _ValidDesign(BaseModel):
    text: str


class _ReferenceMeasurements(BaseModel):
    metric: str


class _Measurements(BaseModel):
    referenceMeasurements: Optional[list[_ReferenceMeasurements]]


class _LocalisedCommunication(BaseModel):
    languageCode: str
    packageMeasurements: Optional[list[_PackageMeasurement]]
    media: list[_Media]
    productName: str
    productType: _ProductType
    validDesign: Optional[_ValidDesign]
    measurements: Optional[_Measurements]


class _ChildItem(BaseModel):
    quantity: int
    itemKey: _ItemKey


class _IngkaItem(BaseModel):
    itemKey: _ItemKey
    localisedCommunications: list[_LocalisedCommunication]
    childItems: Optional[list[_ChildItem]]


class IngkaItemsResponse(BaseModel):
    data: list[_IngkaItem]


def get_localised_communication(comms: list[_LocalisedCommunication]):
    for comm in comms:
        if comm.languageCode == Constants.LANGUAGE_CODE:
            return comm
    raise ParsingError("Cannot find appropriate localized communication")


def _parse_russian_product_name(product_name: str):
    if not re.findall(r"[А-яЁё ]+", product_name):  # Russian text found
        # No russian text found: 'MARABOU'
        return product_name

    if re.findall(r"\d+", product_name):
        # Has numbers in itself: 'IKEA 365+ ИКЕА/365+', 'VINTER 2021 ВИНТЕР 2021'
        if matches := re.findall(r"^[^А-яЁё]+?([А-яЁё].*)", product_name):
            product_name = matches[0]
    else:
        # Covers cases like: 'BESTÅ БЕСТО / EKET ЭКЕТ'
        product_name = re.sub(r"[^А-яЁё /+]+", "", product_name)
        product_name = re.sub(r"\s+", " ", product_name)
        product_name = re.sub(r"^ | $", "", product_name)

    return product_name


def get_name(comm: _LocalisedCommunication):
    product_name = _parse_russian_product_name(comm.productName)
    product_type = comm.productType.name.capitalize()
    design = comm.validDesign.text if comm.validDesign else None

    if (
        comm.measurements
        and comm.measurements.referenceMeasurements
        and len(comm.measurements.referenceMeasurements) > 0
        and comm.measurements.referenceMeasurements[0].metric
    ):
        measurements = comm.measurements.referenceMeasurements[0].metric
    else:
        measurements = None

    return ", ".join(
        part for part in (product_name, product_type, design, measurements) if part
    )


def get_image_url(comm: _LocalisedCommunication):
    for media in comm.media:
        if media.typeName != "MAIN_PRODUCT_IMAGE":
            continue
        for v in media.variants:
            if v.quality == "S5":
                return v.href
    return comm.media[0].variants[0].href


def get_weight(comm: _LocalisedCommunication):
    if not comm.packageMeasurements:
        return 0.0
    for m in comm.packageMeasurements:
        if m.type == "WEIGHT":
            return m.valueMetric
    return 0.0


def get_child_items(child_items: list[_ChildItem] | None) -> list[ChildItemDict]:
    if not child_items:
        return []

    return [
        ChildItemDict(
            item_code=child.itemKey.itemNo,
            item_name=None,
            weight=0.0,
            qty=child.quantity,
        )
        for child in child_items
    ]


def parse_item(item: _IngkaItem):
    comm = get_localised_communication(item.localisedCommunications)
    return IngkaItemDict(
        is_combination=get_is_combination_from_item_type(item.itemKey.itemType),
        item_code=item.itemKey.itemNo,
        name=get_name(comm),
        image_url=get_image_url(comm),
        weight=get_weight(comm),
        child_items=get_child_items(item.childItems),
    )


def main(response: dict[str, Any]):
    parsed_resp = IngkaItemsResponse(**response)
    for item in parsed_resp.data:
        yield parse_item(item)
