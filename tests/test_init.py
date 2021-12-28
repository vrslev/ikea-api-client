from __future__ import annotations

import pytest

import ikea_api
from ikea_api import IKEA
from ikea_api._constants import Constants
from ikea_api._endpoints.cart import Cart
from ikea_api._endpoints.purchases import Purchases
from ikea_api._endpoints.search import SearchType


@pytest.mark.parametrize(
    ("country_code", "language_code"), (("ru", "ru"), (None, None), ("us", "en"))
)
def test_core_init_country_lang_codes_with_args(
    country_code: str | None, language_code: str | None
):
    if country_code and language_code:
        IKEA(country_code=country_code, language_code=language_code)
    assert Constants.COUNTRY_CODE == country_code or "ru"
    assert Constants.LANGUAGE_CODE == language_code or "ru"
    Constants.COUNTRY_CODE = Constants.LANGUAGE_CODE = "ru"


def test_core_init_country_lang_codes_without_args():
    IKEA()
    assert Constants.COUNTRY_CODE == "ru"
    assert Constants.LANGUAGE_CODE == "ru"


@pytest.mark.parametrize(("token"), ("random token string", None))
def test_core_init_token(token: str | None):
    ikea = IKEA(token=token)
    assert ikea.token == token


@pytest.fixture
def core():
    return IKEA(token="test")  # nosec


def test_core_login_as_guest(monkeypatch: pytest.MonkeyPatch, core: IKEA):
    called = False

    def mock_get_guest_token():
        nonlocal called
        called = True

    monkeypatch.setattr(ikea_api, "get_guest_token", mock_get_guest_token)
    core.login_as_guest()
    assert called


def test_core_cart(core: IKEA):
    old_cart = core.cart
    assert hasattr(core, "_cart")
    assert core.cart == old_cart
    assert type(core.cart) == Cart
    assert core.cart.token == core.token


def test_core_order_capture(monkeypatch: pytest.MonkeyPatch, core: IKEA):
    exp_zip_code = "101000"
    exp_state_code = "10100"
    called = False

    class MockOrderCapture:
        def __init__(self, token: str, zip_code: str, state_code: str | None):
            nonlocal called
            called = True
            assert token == core.token
            assert zip_code == exp_zip_code
            assert state_code == exp_state_code

    monkeypatch.setattr(ikea_api, "OrderCapture", MockOrderCapture)
    order_capture = core.order_capture(zip_code=exp_zip_code, state_code=exp_state_code)
    assert isinstance(order_capture, MockOrderCapture)
    assert called
    called = False

    # Ensure we don't have same `OrderCapture` instance
    with pytest.raises(AssertionError):
        order_capture = core.order_capture(zip_code="111000")
    assert called


def test_core_purchases(core: IKEA):
    old_purchases = core.purchases
    assert hasattr(core, "_purchases")
    assert core.purchases == old_purchases
    assert type(core.purchases) == Purchases
    assert core.purchases.token == core.token


def test_core_search(monkeypatch: pytest.MonkeyPatch, core: IKEA):
    exp_query = "Billy"
    exp_limit = 10
    exp_types: list[SearchType] = ["PRODUCT", "CONTENT"]
    called = False

    class MockSearch:
        def __call__(self, query: str, limit: int, types: list[SearchType]):
            assert query == exp_query
            assert limit == exp_limit
            assert types == exp_types

            nonlocal called
            called = True

    monkeypatch.setattr(ikea_api, "Search", MockSearch)
    core.search(exp_query, limit=exp_limit, types=exp_types)
    assert called
