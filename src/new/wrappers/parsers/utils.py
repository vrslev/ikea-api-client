from __future__ import annotations

from typing import Any

from ikea_api._constants import Constants


def translate_from_dict(dictionary: dict[str, dict[str, Any]], v: str):
    lang_dict = dictionary.get(Constants.LANGUAGE_CODE)
    if lang_dict is None:
        return v
    return lang_dict.get(v, v)
