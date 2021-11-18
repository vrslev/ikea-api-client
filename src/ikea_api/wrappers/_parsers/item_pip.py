from typing import Any

from pydantic import BaseModel, HttpUrl

from ikea_api.wrappers import types
from ikea_api.wrappers._parsers.item_base import ItemCode


class Catalog(BaseModel):
    name: str
    url: HttpUrl


class CatalogRef(BaseModel):
    elements: list[Catalog]


class CatalogRefs(BaseModel):
    products: CatalogRef


class PipItem(BaseModel):
    id: ItemCode
    priceNumeral: int
    pipUrl: HttpUrl
    catalogRefs: CatalogRefs


def get_category_name_and_url(catalog_refs: CatalogRefs):
    return catalog_refs.products.elements[0].name, catalog_refs.products.elements[0].url


def main(response: dict[str, Any]):
    parsed_item = PipItem(**response)
    category_name, category_url = get_category_name_and_url(parsed_item.catalogRefs)
    return types.PipItemDict(
        item_code=parsed_item.id,
        price=parsed_item.priceNumeral,
        url=parsed_item.pipUrl,
        category_name=category_name,
        category_url=category_url,
    )
