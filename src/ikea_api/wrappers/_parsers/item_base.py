import sys
from typing import Any

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


class ItemCode(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            if not v.isnumeric():
                raise ValueError("invalid item code format")
            return v
        raise TypeError("string required")


ItemType = Literal["ART", "SPR"]


def get_is_combination_from_item_type(item_type: ItemType):
    assert item_type in ("ART", "SPR"), "Item type should be ART or SPR"
    return item_type == "SPR"
