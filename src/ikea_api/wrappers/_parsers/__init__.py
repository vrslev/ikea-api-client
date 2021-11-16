from __future__ import annotations

from typing import Any

from box import Box, BoxList


def get_box(d: dict[Any, Any]):
    return Box(d, default_box=True, default_box_no_key_error=True)


def get_box_list(l: list[dict[Any, Any]]) -> list[Box]:
    return BoxList(l, default_box=True, default_box_no_key_error=True)
