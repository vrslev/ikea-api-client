import pytest

from ikea_api.constants import Constants
from ikea_api.endpoints.rotera_item import RoteraItem, build_url
from ikea_api.exceptions import APIError
from tests.conftest import EndpointTester, MockResponseInfo


def test_build_url():
    item_code = "30457903"
    expected = "/30457903.json"
    assert build_url(item_code) == expected


@pytest.fixture
def rotera_item(constants: Constants):
    return RoteraItem(constants)


def test_rotera_item_prepare(rotera_item: RoteraItem):
    item_code = "11111111"
    t = EndpointTester(rotera_item.get_item(item_code))
    req = t.prepare()

    assert req.url == build_url(item_code)


def test_rotera_item_not_found(rotera_item: RoteraItem):
    item_code = "11111111"
    t = EndpointTester(rotera_item.get_item(item_code))
    t.prepare()

    with pytest.raises(APIError):
        t.parse(MockResponseInfo(status_code=404))


def test_rotera_item_exists(rotera_item: RoteraItem):
    item_code = "11111111"
    t = EndpointTester(rotera_item.get_item(item_code))
    t.prepare()

    assert t.parse(MockResponseInfo(json_="ok")) == "ok"
