from new.constants import Constants
from new.endpoints import ingka_items
from tests.new.conftest import EndpointTester


def test_ingka_items(constants: Constants):
    item_codes = ["11111111", "22222222"]
    t = EndpointTester(ingka_items.API(constants).get_items(item_codes))

    request_info = t.prepare()
    assert request_info.params == {"itemNos": item_codes}

    t.assert_json_returned()
