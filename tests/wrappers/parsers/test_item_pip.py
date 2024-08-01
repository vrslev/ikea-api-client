from __future__ import annotations

from typing import Any

import pytest
from ikea_api.wrappers.parsers.pip_item import (
    Catalog,
    CatalogRef,
    CatalogRefs,
    get_category_name_and_url,
    parse_pip_item,
)
from pydantic import HttpUrl, ValidationError

from tests.conftest import TestData


def generate_catalog_refs(name: str, url: str):
    return CatalogRefs(products=CatalogRef(elements=[Catalog(name=name, url=url)]))  # type: ignore


def test_get_category_name_and_url_passes():
    name, url = "Книжные шкафы", "https://www.ikea.com/ru/ru/cat/knizhnye-shkafy-10382/"
    assert get_category_name_and_url(generate_catalog_refs(name, url)) == (
        name,
        HttpUrl(url), # pyright: ignore[reportCallIssue]
    )


def test_get_category_name_and_url_raises():
    name, url = "Книжные шкафы", "not a url"
    with pytest.raises(ValidationError):
        generate_catalog_refs(name, url)


@pytest.mark.parametrize("test_data_response", TestData.item_pip)
def test_main(test_data_response: dict[str, Any]):
    parse_pip_item(test_data_response)
