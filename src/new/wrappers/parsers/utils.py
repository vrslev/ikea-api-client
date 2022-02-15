from __future__ import annotations

from typing import Any

from new.constants import Constants


def translate_from_dict(
    constants: Constants, dictionary: dict[str, dict[str, Any]], v: str
):
    lang_dict = dictionary.get(constants.language)
    if lang_dict is None:
        return v
    return lang_dict.get(v, v)
