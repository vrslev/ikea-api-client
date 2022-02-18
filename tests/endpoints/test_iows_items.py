from typing import Any

import pytest

from ikea_api.constants import Constants
from ikea_api.endpoints.iows_items import API
from ikea_api.exceptions import ItemFetchError, WrongItemCodeError
from tests.conftest import EndpointTester, MockResponseInfo


@pytest.fixture
def iows_items(constants: Constants):
    return API(constants)


@pytest.fixture
def iows_tester(iows_items: API):
    return EndpointTester(iows_items.get_items(["11111111"]))


def test_one_first_time(iows_tester: EndpointTester):
    req = iows_tester.prepare()
    assert "SPR" not in req.url
    data = "foo"
    assert iows_tester.parse(MockResponseInfo(json_={"RetailItemComm": data})) == [data]


def test_one_second_time(iows_tester: EndpointTester):
    req = iows_tester.prepare()
    assert "SPR" not in req.url

    iows_tester.parse(MockResponseInfo(status_code=404))
    req = iows_tester.prepare()
    assert "SPR" in req.url

    resp = {"RetailItemComm": "foo"}
    iows_tester.parse(MockResponseInfo(json_=resp)) == resp


def test_one_fails(iows_tester: EndpointTester):
    resp = MockResponseInfo(status_code=404)
    iows_tester.parse(resp)

    with pytest.raises(WrongItemCodeError):
        iows_tester.parse(resp)


def build_error_container(errors: Any):
    return {"ErrorList": {"Error": errors}}


@pytest.mark.parametrize(
    "response",
    (
        [{"ErrorCode": {"$": 1100}}],
        {"ErrorCode": {"$": 1100}},
        {"ErrorCode": {}},
        {},
    ),
)
def test_multiple_fail(iows_tester: EndpointTester, response: Any):
    with pytest.raises(ItemFetchError):
        iows_tester.parse(MockResponseInfo(json_=build_error_container(response)))


def build_item_error(**args: Any):
    prep_args = [{"Name": {"$": k}, "Value": {"$": v}} for k, v in args.items()]
    return {
        "ErrorCode": {"$": 1101},
        "ErrorAttributeList": {"ErrorAttribute": prep_args},
    }


@pytest.mark.parametrize("exit_on", (1, 2, 3))
def test_multiple_second_time(iows_tester: EndpointTester, exit_on: int):
    if exit_on == 3:
        payload = [
            build_item_error(ITEM_NO=11111111, ITEM_TYPE="ART"),
            build_item_error(ITEM_NO=33333333, ITEM_TYPE="ART"),
        ]
        iows_tester.parse(MockResponseInfo(json_=build_error_container(payload)))

    if exit_on > 1:
        payload = [build_item_error(ITEM_NO=11111111, ITEM_TYPE="SPR")]
        iows_tester.parse(MockResponseInfo(json_=build_error_container(payload)))

    data = ["foo", "bar", "op"]
    res = iows_tester.parse(
        MockResponseInfo(json_={"RetailItemCommList": {"RetailItemComm": data}})
    )
    assert res == data


def test_no_response_text(iows_tester: EndpointTester):
    iows_tester.parse(MockResponseInfo(text_=""))
