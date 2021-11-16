from __future__ import annotations

import re
from typing import Any, overload


@overload
def parse_item_code(item_code: str | int) -> str:
    ...


@overload
def parse_item_code(item_code: list[str | int] | list[str]) -> list[str]:
    ...


def parse_item_code(item_code: str | int | list[str | int] | list[str]):
    def _parse(item_code: Any):
        found = re.search(r"\d{3}[, .-]{0,2}\d{3}[, .-]{0,2}\d{2}", str(item_code))
        res = ""
        if found:
            try:
                res = re.sub(r"[^0-9]+", "", found[0])
            except TypeError:
                pass
        return res

    err_msg = f"No items parsed: {str(item_code)}"
    if isinstance(item_code, list):
        item_code = list(set(item_code))
        res: list[str] = []
        for i in item_code:
            parsed = _parse(i)
            if parsed:
                res.append(parsed)
        if not res:
            raise ValueError(err_msg)
        return res
    else:
        parsed = _parse(item_code)
        if not parsed:
            raise ValueError(err_msg)
        return parsed
