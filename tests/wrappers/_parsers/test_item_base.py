import pytest

from ikea_api.wrappers._parsers.item_base import (
    ItemType,
    get_is_combination_from_item_type,
)


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
