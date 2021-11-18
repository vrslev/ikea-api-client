from __future__ import annotations

from typing import Any

from ikea_api._constants import Constants


def translate(dictionary: dict[str, dict[str, Any]], v: str):
    if lang_dict := dictionary.get(Constants.LANGUAGE_CODE):
        return lang_dict.get(v, v)
    return v
