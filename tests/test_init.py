from __future__ import annotations

import pytest

from ikea_api import IkeaApi
from ikea_api.constants import Constants


@pytest.mark.parametrize(
    ("country_code", "language_code"), (("ru", "ru"), (None, None), ("us", "en"))
)
def test_core_init_country_lang_codes_with_args(
    country_code: str | None, language_code: str | None
):
    if country_code and language_code:
        IkeaApi(country_code=country_code, language_code=language_code)
    assert Constants.COUNTRY_CODE == country_code or "ru"
    assert Constants.LANGUAGE_CODE == language_code or "ru"


def test_core_init_country_lang_codes_without_args():
    IkeaApi()
    assert Constants.COUNTRY_CODE == "ru"
    assert Constants.LANGUAGE_CODE == "ru"


@pytest.mark.parametrize(("token"), ("random token string", None))
def test_core_init_country_token(token: str | None):
    ikea = IkeaApi(token=token)
    assert ikea._token == token
