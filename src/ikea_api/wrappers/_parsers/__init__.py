from __future__ import annotations

from typing import Any

from box import Box, BoxList

from ikea_api._constants import Constants


def get_box(d: dict[Any, Any]):
    return Box(d, default_box=True, default_box_no_key_error=True)


def get_box_list(l: list[dict[Any, Any]]) -> list[Box]:
    return BoxList(l, default_box=True, default_box_no_key_error=True)


def translate(dictionary: dict[str, dict[str, Any]], v: str):
    if lang_dict := dictionary.get(Constants.LANGUAGE_CODE):
        return lang_dict.get(v, v)
    return v
