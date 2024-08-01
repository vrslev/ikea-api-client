from __future__ import annotations

import pytest

from ikea_api.wrappers.parsers.item_base import (
    ItemType,
    get_is_combination_from_item_type,
    validate_item_code,
)


def test_item_code_validator_value_error():
    with pytest.raises(ValueError, match="invalid item code format"):
        assert validate_item_code("11111.11") == "11111111"


def test_item_code_validator_type_error():
    with pytest.raises(TypeError, match="string required"):
        validate_item_code({})


@pytest.mark.parametrize("v", ("11111111", "111.111.11", "111-111-11", 11111111))
def test_item_code_validator_passes(v: str | int):
    assert validate_item_code(v) == "11111111"


@pytest.mark.parametrize(
    ("item_type", "is_combination"), (("ART", False), ("SPR", True))
)
def test_get_is_combination_from_item_type_passes(
    item_type: ItemType, is_combination: bool
):
    assert get_is_combination_from_item_type(item_type) == is_combination


def test_get_is_combination_from_item_type_raises():
    with pytest.raises(AssertionError, match="Item type should be ART or SPR"):
        assert get_is_combination_from_item_type("not ART or SPR")  # type: ignore
