from __future__ import annotations

import pytest

import ikea_api
from ikea_api import IkeaApi
from ikea_api._constants import Constants


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
def test_core_init_token(token: str | None):
    ikea = IkeaApi(token=token)
    assert ikea.token == token


@pytest.fixture
def core():
    return IkeaApi()


def test_core_login_not_guest(monkeypatch: pytest.MonkeyPatch, core: IkeaApi):
    exp_username = "user"
    exp_password = "pass"  # nosec
    called = False

    def mock_get_authorized_token(username: str, password: str):
        assert username == exp_username
        assert password == exp_password
        nonlocal called
        called = True

    monkeypatch.setattr(ikea_api, "get_authorized_token", mock_get_authorized_token)
    core.login(exp_username, exp_password)
    assert called


def test_core_login_as_guest(monkeypatch: pytest.MonkeyPatch, core: IkeaApi):
    called = False

    def mock_get_guest_token():
        nonlocal called
        called = True

    monkeypatch.setattr(ikea_api, "get_guest_token", mock_get_guest_token)
    core.login_as_guest()
    assert called


def test_core_cart(core: IkeaApi):
    old_cart = core.cart
    assert hasattr(core, "_cart")
    assert core.cart == old_cart
