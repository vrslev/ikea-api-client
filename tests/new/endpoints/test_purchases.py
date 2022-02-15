import pytest

from new.constants import Constants
from new.endpoints.purchases import API, Queries, _build_payload
from tests.new.conftest import EndpointTester


def test_build_payload():
    assert _build_payload("myoperation", "myquery", var1=1, var2=2) == {
        "operationName": "myoperation",
        "variables": {"var1": 1, "var2": 2},
        "query": "myquery",
    }


@pytest.fixture
def purchases(constants: Constants):
    return API(constants, token="mytoken")  # nosec


def test_history(purchases: API):
    take = 3
    skip = 1
    t = EndpointTester(purchases.history(take=take, skip=skip))
    req = t.prepare()

    assert req.method == "POST"
    assert req.url == ""
    assert req.json == _build_payload("History", Queries.history, take=take, skip=skip)

    t.assert_json_returned()


def test_order_info_with_email(purchases: API):
    email = "mail@example.com"

    t = EndpointTester(purchases.order_info(order_number="", email=email))
    req = t.prepare()

    for chunk in req.json:
        assert chunk["variables"]["liteId"] == email

    assert req.headers
    assert "lookup" in req.headers["Referer"]

    t.assert_json_returned()


def test_order_info_no_email(purchases: API):
    order_number = "1111111111"

    t = EndpointTester(purchases.order_info(order_number=order_number))
    req = t.prepare()

    assert req.headers
    assert order_number in req.headers["Referer"]

    t.assert_json_returned()
