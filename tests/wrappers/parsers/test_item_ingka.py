from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.constants import Constants
from ikea_api.exceptions import ParsingError
from ikea_api.wrappers.parsers.ingka_items import (
    get_child_items,
    get_image_url,
    get_localised_communication,
    get_name,
    get_weight,
    parse_ingka_items,
    parse_russian_product_name,
)
from tests.conftest import TestData


def test_get_localised_communication_passes():
    constants = Constants(language="nolang")
    exp_res = SimpleNamespace(languageCode="nolang")
    communications: list[Any] = [
        SimpleNamespace(languageCode="ru"),
        SimpleNamespace(languageCode="en"),
        exp_res,
    ]
    assert get_localised_communication(constants, communications) == exp_res


def test_get_localised_communication_raises():
    constants = Constants(language="nolang")
    communications: list[Any] = [
        SimpleNamespace(languageCode="ru"),
        SimpleNamespace(languageCode="en"),
    ]
    with pytest.raises(
        ParsingError, match="Cannot find appropriate localized communication"
    ):
        get_localised_communication(constants, communications)


@pytest.mark.parametrize(
    ("input", "output"),
    (
        ("MARABOU", "MARABOU"),
        ("IKEA 365+ ИКЕА/365+", "ИКЕА/365+"),
        ("VINTER 2021 ВИНТЕР 2021", "ВИНТЕР 2021"),
        ("BESTÅ БЕСТО / EKET ЭКЕТ", "БЕСТО / ЭКЕТ"),
        ("BESTÅ", "BESTÅ"),
        ("BESTÅ БЕСТО", "БЕСТО"),
    ),
)
def test_parse_russian_product_name(input: str, output: str):
    assert parse_russian_product_name(input) == output


@pytest.mark.parametrize(
    ("product_name", "product_type", "design", "measurements", "exp_result"),
    (
        (
            "EKET ЭКЕТ",
            "комбинация настенных шкафов",
            "белый/светло-зеленый",
            "175x25x70 см",
            "ЭКЕТ, Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
        ),
        (
            "KALLAX КАЛЛАКС",
            "стеллаж",
            "серый/под дерево",
            "77x147 см",
            "КАЛЛАКС, Стеллаж, серый/под дерево, 77x147 см",
        ),
        (
            "FENOMEN ФЕНОМЕН",
            "неароматическая формовая свеча, 5шт",
            "естественный",
            None,
            "ФЕНОМЕН, Неароматическая формовая свеча, 5шт, естественный",
        ),
        ("MARABOU", "шоколад Дайм", None, None, "MARABOU, Шоколад дайм"),
    ),
)
def test_get_name(
    product_name: str,
    product_type: str,
    design: str | None,
    measurements: str | None,
    exp_result: str,
):
    comm: Any = SimpleNamespace(
        productName=product_name,
        productType=SimpleNamespace(name=product_type),
        validDesign=SimpleNamespace(text=design) if design else None,
        measurements=SimpleNamespace(
            referenceMeasurements=[SimpleNamespace(metric=measurements)]
        )
        if measurements
        else None,
    )

    assert get_name(comm) == exp_result


def test_get_image_url_not_main_image():
    exp_value = "some href"
    comm: Any = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="not main product image",
                variants=[SimpleNamespace(href=exp_value)],
            ),
            SimpleNamespace(
                typeName="not main product image",
                variants=[SimpleNamespace(href="not exp_value")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value


def test_get_image_url_main_image_not_s5():
    exp_value = "some href"
    comm: Any = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href=exp_value, quality="S1")],
            ),
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href="not exp_value", quality="S2")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value


def test_get_image_url_main_image_s5():
    exp_value = "some href"
    comm: Any = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href="not exp_value", quality="S1")],
            ),
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href=exp_value, quality="S5")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value


def test_get_weight_no_package_measurements():
    comm: Any = SimpleNamespace(packageMeasurements=None)
    assert get_weight(comm) == 0.0


def test_get_weight_no_values():
    comm: Any = SimpleNamespace(packageMeasurements=[])
    assert get_weight(comm) == 0.0


def test_get_weight_no_weight():
    comm: Any = SimpleNamespace(
        packageMeasurements=[SimpleNamespace(type="not weight")]
    )
    assert get_weight(comm) == 0.0


def test_get_weight_success():
    comm: Any = SimpleNamespace(
        packageMeasurements=[
            SimpleNamespace(type="not weight", valueMetric="not exp_value"),
            SimpleNamespace(type="WEIGHT", valueMetric=5.0),
            SimpleNamespace(type="WEIGHT", valueMetric=6.0),
        ]
    )
    assert get_weight(comm) == 11.0


@pytest.mark.parametrize("input", ([], None))
def test_get_child_items_no_input(input: list[Any] | None):
    assert get_child_items(input) == []


def test_get_child_items_success():
    exp_result = {"11111111": 1, "22222222": 3}
    child_items: list[Any] = [
        SimpleNamespace(itemKey=SimpleNamespace(itemNo=item_code), quantity=qty)
        for item_code, qty in exp_result.items()
    ]

    for child in get_child_items(child_items):
        assert child.qty == exp_result[child.item_code]
        assert child.weight == 0.0
        assert child.name is None


@pytest.mark.parametrize("test_data_response", TestData.item_ingka)
def test_main(constants: Constants, test_data_response: dict[str, Any]):
    list(parse_ingka_items(constants, test_data_response))
