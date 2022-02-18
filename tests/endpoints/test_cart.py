from typing import Any, Callable

import pytest

from ikea_api.abc import EndpointInfo
from ikea_api.constants import Constants
from ikea_api.endpoints.cart import API, Mutations, Queries, _convert_items
from tests.conftest import EndpointTester

in_items = {"11111111": 1, "22222222": 2}
out_items = [
    {"itemNo": "11111111", "quantity": 1},
    {"itemNo": "22222222", "quantity": 2},
]


def test_cart_convert_items():
    assert _convert_items(in_items) == out_items


@pytest.fixture
def cart(constants: Constants):
    return API(constants, token="mytoken")  # nosec


def test_cart_req(cart: API):
    query = "myquery"
    variables = {"ta": "da", "pa": "ga"}

    t = EndpointTester(cart._req(query, **variables))
    req = t.prepare()

    assert req.json["query"] == query
    assert req.json["variables"] == {"languageCode": cart.const.language, **variables}

    t.assert_json_returned()


def assert_req_called_with(endpoint: EndpointInfo[Any], query: str, **variables: Any):
    t = EndpointTester(endpoint)
    req = t.prepare()
    assert req.json["query"] == query
    del req.json["variables"]["languageCode"]
    assert req.json["variables"] == variables


@pytest.mark.parametrize(
    ("method", "query"),
    (
        (API.show, Queries.cart),
        (API.clear, Mutations.clear_items),
        (API.clear_coupon, Mutations.clear_coupon),
    ),
)
def test_cart_no_vars_methods(cart: API, method: Callable[..., Any], query: str):
    assert_req_called_with(method(cart), query)


@pytest.mark.parametrize(
    ("method", "query"),
    ((API.add_items, Mutations.add_items), (API.update_items, Mutations.update_items)),
)
def test_cart_add_update_items(cart: API, method: Callable[..., Any], query: str):
    assert_req_called_with(method(cart, in_items), query, items=out_items)


def test_cart_copy_items(cart: API):
    source_user_id = "myuserid"
    assert_req_called_with(
        cart.copy_items(source_user_id=source_user_id),
        Mutations.copy_items,
        sourceUserId=source_user_id,
    )


def test_cart_remove_items(cart: API):
    item_codes = ["11111111"]
    assert_req_called_with(
        cart.remove_items(item_codes), Mutations.remove_items, itemNos=item_codes
    )


def test_cart_set_coupon(cart: API):
    code = "11"
    assert_req_called_with(cart.set_coupon(code), Mutations.set_coupon, code=code)
