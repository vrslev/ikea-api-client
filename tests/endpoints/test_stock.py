from ikea_api.constants import Constants
from ikea_api.endpoints.stock import Stock
from tests.conftest import EndpointTester, MockResponseInfo


def test_stock_prepare(constants: Constants):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))
    req = t.prepare()

    assert req.params
    assert req.params["itemNos"] == [item_code]


def test_stock_parse(constants: Constants):
    item_code = "11111111"
    t = EndpointTester(Stock(constants).get_stock(item_code))
    assert t.parse(MockResponseInfo(json_="ok")) == "ok"
