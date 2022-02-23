from typing import Any

import pytest

from ikea_api.constants import Constants
from ikea_api.endpoints.stock import Stock
from ikea_api.exceptions import ItemFetchError
from tests.conftest import EndpointTester, MockResponseInfo


def test_stock_prepare(constants: Constants):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))
    req = t.prepare()

    assert req.params
    assert req.params["itemNos"] == [item_code]


@pytest.mark.parametrize(
    "v",
    (
        {"errors": {}},
        {"errors": []},
        {"errors": [{"code": 404, "message": "Not found", "details": []}]},
    ),
)
def test_stock_raises_without_item_code(constants: Constants, v: Any):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))

    with pytest.raises(ItemFetchError) as exc:
        t.parse(MockResponseInfo(json_=v))

    assert item_code not in str(exc.value.args)


def test_stock_raises_with_item_code(constants: Constants):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))
    response = {
        "availabilities": None,
        "errors": [
            {
                "code": 404,
                "message": "Not found",
                "details": {
                    "classUnitCode": "RU",
                    "classUnitType": "RU",
                    "itemNo": item_code,
                },
            }
        ],
    }
    with pytest.raises(ItemFetchError) as exc:
        t.parse(MockResponseInfo(json_=response))
    assert item_code in exc.value.args


def test_stock_passes(constants: Constants):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))
    assert t.parse(MockResponseInfo(json_="ok")) == "ok"
