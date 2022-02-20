import pytest

from ikea_api.constants import Constants
from ikea_api.endpoints.purchases import Purchases, Queries, _build_payload
from tests.conftest import EndpointTester


def test_build_payload():
    assert _build_payload("myoperation", "myquery", var1=1, var2=2) == {
        "operationName": "myoperation",
        "variables": {"var1": 1, "var2": 2},
        "query": "myquery",
    }


@pytest.fixture
def purchases(constants: Constants):
    return Purchases(constants, token="mytoken")  # nosec


def test_history(purchases: Purchases):
    take = 3
    skip = 1
    t = EndpointTester(purchases.history(take=take, skip=skip))
    req = t.prepare()
    assert req.json == _build_payload("History", Queries.history, take=take, skip=skip)

    t.assert_json_returned()


def test_order_info_with_email(purchases: Purchases):
    email = "mail@example.com"

    t = EndpointTester(purchases.order_info(order_number="", email=email))
    req = t.prepare()

    for chunk in req.json:
        assert chunk["variables"]["liteId"] == email

    assert req.headers
    assert "lookup" in req.headers["Referer"]

    t.assert_json_returned()


def test_order_info_no_email(purchases: Purchases):
    order_number = "1111111111"

    t = EndpointTester(purchases.order_info(order_number=order_number))
    req = t.prepare()

    assert req.headers
    assert order_number in req.headers["Referer"]

    t.assert_json_returned()
