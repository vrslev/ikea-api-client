from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, HttpUrl

from ikea_api.wrappers import types
from ikea_api.wrappers.parsers.item_base import ItemCode


class Catalog(BaseModel):
    name: str
    url: HttpUrl


class CatalogRef(BaseModel):
    elements: List[Catalog]


class CatalogRefs(BaseModel):
    products: Optional[CatalogRef]


class ResponsePipItem(BaseModel):
    id: ItemCode
    priceNumeral: int
    pipUrl: HttpUrl
    catalogRefs: CatalogRefs


def get_category_name_and_url(catalog_refs: CatalogRefs):
    if not catalog_refs.products:
        return None, None
    return catalog_refs.products.elements[0].name, catalog_refs.products.elements[0].url


def parse_pip_item(response: dict[str, Any]) -> types.PipItem | None:
    if not response:
        return
    parsed_item = ResponsePipItem(**response)
    category_name, category_url = get_category_name_and_url(parsed_item.catalogRefs)
    return types.PipItem(
        item_code=parsed_item.id,
        price=parsed_item.priceNumeral,
        url=parsed_item.pipUrl,
        category_name=category_name,
        category_url=category_url,
    )
