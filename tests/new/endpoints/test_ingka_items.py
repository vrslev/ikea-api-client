from new.constants import Constants
from new.endpoints import ingka_items
from tests.new.conftest import EndpointTester


def test_ingka_items(constants: Constants):
    item_codes = ["11111111", "22222222"]
    c = EndpointTester(ingka_items.API(constants).get_items(item_codes))

    request_info = c.prepare()
    assert request_info.method == "GET"
    assert request_info.params == {"itemNos": item_codes}

    c.assert_json_returned()
