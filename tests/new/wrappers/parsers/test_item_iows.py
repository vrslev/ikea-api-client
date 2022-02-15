from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable

import pytest

from new.constants import Constants
from new.wrappers import types
from new.wrappers.parsers.item_iows import (
    Catalog,
    CatalogElement,
    CatalogElementList,
    get_category_name_and_url,
    get_child_items,
    get_image_url,
    get_price,
    get_rid_of_dollars,
    get_url,
    get_weight,
    main,
    parse_weight,
)
from tests.conftest import TestData


def test_get_rid_of_dollars():
    assert get_rid_of_dollars({"name": {"$": "The Name"}}) == {"name": "The Name"}


def test_get_image_url_filtered(constants: Constants):
    assert (
        get_image_url(
            constants,
            [  # type: ignore
                SimpleNamespace(ImageType="LINE DRAWING"),
                SimpleNamespace(
                    ImageType="not LINE DRAWING", ImageUrl="somename.notpngorjpg"
                ),
            ],
        )
        is None
    )


def test_get_image_url_no_images(constants: Constants):
    assert get_image_url(constants, []) is None


@pytest.mark.parametrize("ext", (".png", ".jpg", ".PNG", ".JPG"))
def test_get_image_url_matches(constants: Constants, ext: str):
    image: Callable[[str], SimpleNamespace] = lambda ext: SimpleNamespace(
        ImageType="not line drawing", ImageSize="S5", ImageUrl="somename" + ext
    )
    assert (
        get_image_url(constants, [image(ext), image(".notpngjpg")])  # type: ignore
        == f"{constants.base_url}somename{ext}"
    )


def test_get_image_url_first(constants: Constants):
    url = "somename.jpg"
    images = [
        SimpleNamespace(ImageType="not line drawing", ImageSize="S4", ImageUrl=url)
    ]
    assert get_image_url(constants, images) == constants.base_url + url  # type: ignore


@pytest.mark.parametrize(
    ("input", "output"),
    (
        ("10.3 кг", 10.3),
        ("10.45 кг", 10.45),
        ("10 кг", 10.0),
        ("9.415 кг", 9.415),
        ("some string", 0.0),
    ),
)
def test_parse_weight(input: str, output: float):
    assert parse_weight(input) == output


def test_get_weight_no_measurements():
    assert get_weight([]) == 0.0


def test_get_weight_no_weight():
    measurements = [
        SimpleNamespace(
            PackageMeasureType="not WEIGHT", PackageMeasureTextMetric="10.45 м"
        )
    ]
    assert get_weight(measurements) == 0.0  # type: ignore


def test_get_weight_with_input():
    measurements = [
        SimpleNamespace(
            PackageMeasureType="not WEIGHT", PackageMeasureTextMetric="10.45 м"
        ),
        SimpleNamespace(
            PackageMeasureType="WEIGHT", PackageMeasureTextMetric="9.67 кг"
        ),
        SimpleNamespace(
            PackageMeasureType="WEIGHT", PackageMeasureTextMetric="0.33 кг"
        ),
    ]
    assert get_weight(measurements) == 10.0  # type: ignore


def test_get_child_items_no_input():
    assert get_child_items([]) == []


def test_get_child_items_with_input():
    child_items = [
        SimpleNamespace(
            Quantity=10,
            ItemNo="70299474",
            ProductName="БЕСТО",
            ProductTypeName="каркас",
            ItemMeasureReferenceTextMetric=None,
            ValidDesignText=None,
            RetailItemCommPackageMeasureList=SimpleNamespace(
                RetailItemCommPackageMeasure=[
                    SimpleNamespace(
                        PackageMeasureType="WEIGHT", PackageMeasureTextMetric="17.95 кг"
                    )
                ]
            ),
        ),
        SimpleNamespace(
            Quantity=4,
            ItemNo="70299443",
            ProductName="БЕСТО",
            ProductTypeName="нажимные плавно закрывающиеся петли",
            ItemMeasureReferenceTextMetric=None,
            ValidDesignText=None,
            RetailItemCommPackageMeasureList=SimpleNamespace(
                RetailItemCommPackageMeasure=[
                    SimpleNamespace(
                        PackageMeasureType="WEIGHT", PackageMeasureTextMetric="13.19 кг"
                    )
                ]
            ),
        ),
    ]
    exp_result = [
        types.ChildItem(
            item_code="70299474", name="БЕСТО, Каркас", weight=17.95, qty=10
        ),
        types.ChildItem(
            item_code="70299443",
            name="БЕСТО, Нажимные плавно закрывающиеся петли",
            weight=13.19,
            qty=4,
        ),
    ]
    assert get_child_items(child_items) == exp_result  # type: ignore


def test_get_price_no_input():
    assert get_price([]) == 0


def test_get_price_not_list_zero():
    assert get_price(SimpleNamespace(Price=0)) == 0  # type: ignore


def test_get_price_not_list_not_zero():
    assert get_price(SimpleNamespace(Price=10)) == 10  # type: ignore


def test_get_price_list():
    assert get_price([SimpleNamespace(Price=5), SimpleNamespace(Price=20)]) == 5  # type: ignore


@pytest.mark.parametrize(
    ("item_code", "is_combination", "exp_res"),
    (
        ("11111111", False, f"/p/-11111111"),
        ("11111111", True, f"/p/-s11111111"),
    ),
)
def test_get_url(
    constants: Constants, item_code: str, is_combination: bool, exp_res: str
):
    assert (
        get_url(constants, item_code, is_combination)
        == f"{constants.local_base_url}{exp_res}"
    )


def test_get_category_name_and_url_no_category(constants: Constants):
    assert get_category_name_and_url(
        constants,
        [SimpleNamespace(CatalogElementList=SimpleNamespace(CatalogElement=[]))],  # type: ignore
    ) == (None, None)


def test_get_category_name_and_url_no_categories(constants: Constants):
    assert get_category_name_and_url(constants, []) == (None, None)


def test_get_category_name_and_url_not_list(constants: Constants):
    assert get_category_name_and_url(
        constants,
        Catalog(
            CatalogElementList=CatalogElementList(
                CatalogElement=CatalogElement(
                    CatalogElementName="name", CatalogElementId="id"
                )
            )
        ),
    ) == ("name", "https://www.ikea.com/ru/ru/cat/-id")


@pytest.mark.parametrize(("name", "id"), (("value", {}), ({}, "value"), ({}, {})))
def test_get_category_name_and_url_name_or_id_is_dict(
    constants: Constants, name: str | dict[Any, Any], id: str | dict[Any, Any]
):
    assert get_category_name_and_url(
        constants,
        [  # type: ignore
            SimpleNamespace(
                CatalogElementList=SimpleNamespace(
                    CatalogElement=SimpleNamespace(
                        CatalogElementName=name, CatalogElementId=id
                    )
                )
            )
        ],
    ) == (None, None)


def test_get_category_name_and_url_passes(constants: Constants):
    catalogs_first_el = [
        SimpleNamespace(
            CatalogElementList=SimpleNamespace(
                CatalogElement=SimpleNamespace(
                    CatalogElementName="name", CatalogElementId="id"
                )
            )
        )
    ]
    exp_res = (
        "name",
        f"{constants.local_base_url}/cat/-id",
    )
    assert get_category_name_and_url(constants, catalogs_first_el) == exp_res  # type: ignore
    catalogs_second_el = [SimpleNamespace()] + catalogs_first_el
    assert get_category_name_and_url(constants, catalogs_second_el) == exp_res  # type: ignore


@pytest.mark.parametrize("test_data_response", TestData.item_iows)
def test_main(constants: Constants, test_data_response: dict[str, Any]):
    main(constants, test_data_response)
