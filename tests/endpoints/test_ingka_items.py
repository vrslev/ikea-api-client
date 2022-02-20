from typing import Any

import pytest

from ikea_api import ItemFetchError
from ikea_api.constants import Constants
from ikea_api.endpoints import ingka_items
from tests.conftest import EndpointTester, MockResponseInfo


def test_ingka_items_passes(constants: Constants):
    item_codes = ["11111111", "22222222"]
    t = EndpointTester(ingka_items.IngkaItems(constants).get_items(item_codes))

    request_info = t.prepare()
    assert request_info.params == {"itemNos": item_codes}

    t.assert_json_returned()


@pytest.mark.parametrize(
    "v",
    (
        {"error": {}},
        {"error": []},
        {
            "error": {
                "code": 404,
                "message": "no item numbers were found",
                "details": [],
            }
        },
    ),
)
def test_ingka_items_raises_no_item_code(constants: Constants, v: Any):
    t = EndpointTester(ingka_items.IngkaItems(constants).get_items([]))
    with pytest.raises(ItemFetchError):
        t.parse(MockResponseInfo(json_=v))


def test_ingka_items_raises_with_item_code(constants: Constants):
    v = {
        "error": {
            "code": 404,
            "message": "no item numbers were found",
            "details": [
                {
                    "@type": "type.googleapis.com/google.protobuf.Struct",
                    "value": {"keys": ["11111111"]},
                }
            ],
        }
    }
    t = EndpointTester(ingka_items.IngkaItems(constants).get_items([]))
    with pytest.raises(ItemFetchError):
        t.parse(MockResponseInfo(json_=v))
