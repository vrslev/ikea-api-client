from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, HttpUrl

from ikea_api.wrappers import types
from ikea_api.wrappers._parsers.item_base import ItemCode

__all__ = ["main"]


class Catalog(BaseModel):
    name: str
    url: HttpUrl


class CatalogRef(BaseModel):
    elements: List[Catalog]


class CatalogRefs(BaseModel):
    products: CatalogRef


class ResponsePipItem(BaseModel):
    id: ItemCode
    priceNumeral: int
    pipUrl: HttpUrl
    catalogRefs: CatalogRefs


def get_category_name_and_url(catalog_refs: CatalogRefs):
    return catalog_refs.products.elements[0].name, catalog_refs.products.elements[0].url


def main(response: dict[str, Any]):
    parsed_item = ResponsePipItem(**response)
    category_name, category_url = get_category_name_and_url(parsed_item.catalogRefs)
    return types.PipItem(
        item_code=parsed_item.id,
        price=parsed_item.priceNumeral,
        url=parsed_item.pipUrl,
        category_name=category_name,
        category_url=category_url,
    )
