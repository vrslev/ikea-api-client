from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ikea_api.wrappers._parsers.item_pip import (
    Catalog,
    CatalogRef,
    CatalogRefs,
    get_category_name_and_url,
    main,
)
from tests.conftest import get_all_data_files_in_directory


def generate_catalog_refs(name: str, url: str):
    return CatalogRefs(products=CatalogRef(elements=[Catalog(name=name, url=url)]))


def test_get_category_name_and_url_passes():
    name, url = "Книжные шкафы", "https://www.ikea.com/ru/ru/cat/knizhnye-shkafy-10382/"
    assert get_category_name_and_url(generate_catalog_refs(name, url)) == (name, url)


def test_get_category_name_and_url_raises():
    name, url = "Книжные шкафы", "not a url"
    with pytest.raises(ValidationError):
        generate_catalog_refs(name, url)


test_data = get_all_data_files_in_directory("item_pip")


@pytest.mark.parametrize("test_data_response", test_data)
def test_main(test_data_response: dict[str, Any]):
    main(test_data_response)
