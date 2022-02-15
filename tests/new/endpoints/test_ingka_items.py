import pytest

from new.constants import Constants
from new.endpoints import ingka_items
from tests.new.conftest import EndpointTester


@pytest.fixture
def ingka_items_api(constants: Constants):
    return ingka_items.API(constants)


def test_get_items(ingka_items_api: ingka_items.API):
    item_codes = ["11111111", "22222222"]
    c = EndpointTester(ingka_items_api.get_items(item_codes))

    request_info = c.prepare()
    assert request_info.method == "GET"
    assert request_info.params == {"itemNos": item_codes}

    c.assert_json_returned()
