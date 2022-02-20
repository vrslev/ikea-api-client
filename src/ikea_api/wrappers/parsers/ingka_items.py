from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional

from pydantic import BaseModel

from ikea_api.constants import Constants
from ikea_api.exceptions import ParsingError
from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.item_base import (
    ItemCode,
    ItemType,
    get_is_combination_from_item_type,
)


class ItemKey(BaseModel):
    itemType: ItemType
    itemNo: ItemCode


class PackageMeasurement(BaseModel):
    type: str
    valueMetric: float


class MediaVariant(BaseModel):
    quality: str
    href: str


class Media(BaseModel):
    typeName: str
    variants: List[MediaVariant]


class ProductType(BaseModel):
    name: str


class ValidDesign(BaseModel):
    text: str


class ReferenceMeasurements(BaseModel):
    metric: str


class Measurements(BaseModel):
    referenceMeasurements: Optional[List[ReferenceMeasurements]]


class LocalisedCommunication(BaseModel):
    languageCode: str
    packageMeasurements: Optional[List[PackageMeasurement]]
    media: Optional[List[Media]]
    productName: str
    productType: ProductType
    validDesign: Optional[ValidDesign]
    measurements: Optional[Measurements]


class ChildItem(BaseModel):
    quantity: int
    itemKey: ItemKey


class ResponseIngkaItem(BaseModel):
    itemKey: ItemKey
    localisedCommunications: List[LocalisedCommunication]
    childItems: Optional[List[ChildItem]]


class ResponseIngkaItems(BaseModel):
    data: List[ResponseIngkaItem]


def get_localised_communication(
    constants: Constants, comms: list[LocalisedCommunication]
) -> LocalisedCommunication:
    for comm in comms:
        if comm.languageCode == constants.language:
            return comm
    raise ParsingError("Cannot find appropriate localized communication")


def parse_russian_product_name(product_name: str) -> str:
    if not re.findall(r"[А-яЁё ]+", product_name):  # Russian text found
        # No russian text found: 'MARABOU'
        return product_name

    if re.findall(r"\d+", product_name):
        # Has numbers in itself: 'IKEA 365+ ИКЕА/365+', 'VINTER 2021 ВИНТЕР 2021'
        matches = re.findall(r"^[^А-яЁё]+?([А-яЁё].*)", product_name)
        if matches:
            product_name = matches[0]
    else:
        # Covers cases like: 'BESTÅ БЕСТО / EKET ЭКЕТ'
        product_name = re.sub(r"[^А-яЁё /+]+", "", product_name)
        product_name = re.sub(r"\s+", " ", product_name)
        product_name = re.sub(r"^ | $", "", product_name)

    return product_name


def get_name(comm: LocalisedCommunication) -> str:
    product_name = parse_russian_product_name(comm.productName)
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


def get_image_url(comm: LocalisedCommunication) -> str | None:
    if comm.media is None:
        return

    for media in comm.media:
        if media.typeName != "MAIN_PRODUCT_IMAGE":
            continue
        for v in media.variants:
            if v.quality == "S5":
                return v.href
    return comm.media[0].variants[0].href


def get_weight(comm: LocalisedCommunication) -> float:
    weight = 0.0
    if not comm.packageMeasurements:
        return weight

    for m in comm.packageMeasurements:
        if m.type == "WEIGHT":
            weight += m.valueMetric
    return weight


def get_child_items(child_items: list[ChildItem] | None) -> list[types.ChildItem]:
    if not child_items:
        return []

    return [
        types.ChildItem(
            item_code=child.itemKey.itemNo,
            name=None,
            weight=0.0,
            qty=child.quantity,
        )
        for child in child_items
    ]


def parse_item(constants: Constants, item: ResponseIngkaItem) -> types.IngkaItem:
    comm = get_localised_communication(constants, item.localisedCommunications)
    return types.IngkaItem(
        is_combination=get_is_combination_from_item_type(item.itemKey.itemType),
        item_code=item.itemKey.itemNo,
        name=get_name(comm),
        image_url=get_image_url(comm),
        weight=get_weight(comm),
        child_items=get_child_items(item.childItems),
    )


def parse_ingka_items(
    constants: Constants, response: dict[str, Any]
) -> Iterable[types.IngkaItem]:
    parsed_resp = ResponseIngkaItems(**response)
    for item in parsed_resp.data:
        yield parse_item(constants, item)
