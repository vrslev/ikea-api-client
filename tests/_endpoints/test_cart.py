from typing import Any

import pytest

from ikea_api import Constants
from ikea_api._endpoints.cart import Cart, Mutations, Queries


@pytest.fixture
def cart():
    return Cart("test_token")


def test_cart_call_api():
    query = "testquery"
    variables = {"testvar1": 1, "testvar2": 2}

    class MockCart(Cart):
        def _post(  # type: ignore
            self,
            endpoint: str | None = None,
            headers: dict[str, str] | None = None,
            json: Any = None,
        ):
            assert endpoint is None
            assert headers is None
            assert json == {
                "query": query,
                "variables": {"languageCode": Constants.LANGUAGE_CODE, **variables},
            }

    cart = MockCart("test_token")
    cart._call_api(query, **variables)


def patch_call_api(cart: Cart, exp_query: str, exp_variables: dict[str, Any]):
    def mock_call_api(query: str, **variables: Any):
        assert query == exp_query
        assert variables == exp_variables
        return "test"

    cart._call_api = mock_call_api  # type: ignore


def test_cart_show(cart: Cart):
    patch_call_api(cart, Queries.cart, {})
    assert cart.show() == "test"


def test_cart_clear(cart: Cart):
    patch_call_api(cart, Mutations.clear_items, {})
    assert cart.clear() == "test"


def test_make_templated_items(cart: Cart):
    items = {"11111111": 1, "22222222": 2}
    assert cart._make_templated_items(items) == [
        {"itemNo": "11111111", "quantity": 1},
        {"itemNo": "22222222", "quantity": 2},
    ]


def test_add_items(cart: Cart):
    items = {"11111111": 1}
    patch_call_api(
        cart, Mutations.add_items, {"items": cart._make_templated_items(items)}
    )
    assert cart.add_items(items) == "test"


def test_update_items(cart: Cart):
    items = {"11111111": 1}
    patch_call_api(
        cart, Mutations.update_items, {"items": cart._make_templated_items(items)}
    )
    assert cart.update_items(items) == "test"


def test_copy_items(cart: Cart):
    source_user_id = "112"
    patch_call_api(cart, Mutations.copy_items, {"sourceUserId": source_user_id})
    assert cart.copy_items(source_user_id) == "test"


def test_remove_items(cart: Cart):
    items = ["11111111", "22222222"]
    patch_call_api(cart, Mutations.remove_items, {"itemNos": items})
    assert cart.remove_items(items) == "test"


def test_set_coupon(cart: Cart):
    code = "11113"
    patch_call_api(cart, Mutations.set_coupon, {"code": code})
    assert cart.set_coupon(code) == "test"


def test_clear_coupon(cart: Cart):
    patch_call_api(cart, Mutations.clear_coupon, {})
    assert cart.clear_coupon() == "test"
