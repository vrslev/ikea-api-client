from typing import Any, Literal

from pydantic import BeforeValidator
from typing_extensions import Annotated

from ikea_api.utils import parse_item_codes


def validate_item_code(value: Any) -> str:
    if isinstance(value, int):
        value = str(value)
    if isinstance(value, str):
        parsed_item_codes = parse_item_codes(value)
        if len(parsed_item_codes) != 1:
            raise ValueError("invalid item code format")
        return parsed_item_codes[0]
    raise TypeError("string required")


ItemCode = Annotated[str, BeforeValidator(validate_item_code)]
ItemType = Literal["ART", "SPR"]


def get_is_combination_from_item_type(item_type: ItemType) -> bool:
    assert item_type in ("ART", "SPR"), "Item type should be ART or SPR"
    return item_type == "SPR"
