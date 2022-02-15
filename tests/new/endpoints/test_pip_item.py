import pytest

from new.constants import Constants
from new.endpoints.pip_item import API, _build_url
from new.exceptions import APIError
from tests.new.conftest import EndpointTester, MockResponseInfo


@pytest.mark.parametrize(
    ("item_code", "is_combination", "expected"),
    (
        ("30457903", False, "/903/30457903.json"),
        ("30457903", True, "/903/s30457903.json"),
    ),
)
def test_build_url(item_code: str, is_combination: bool, expected: str):
    assert _build_url(item_code, is_combination) == expected


@pytest.fixture
def pip_item(constants: Constants):
    return API(constants)


def test_pip_item_prepare(pip_item: API):
    item_code = "11111111"
    is_combination = False
    t = EndpointTester(pip_item.get_item(item_code, is_combination))
    req = t.prepare()

    assert req.method == "GET"
    assert req.url == _build_url(item_code, is_combination)


def test_pip_item_no_retry(pip_item: API):
    item_code = "11111111"
    is_combination = False
    t = EndpointTester(pip_item.get_item(item_code, is_combination))
    t.prepare()

    with pytest.raises(APIError):
        t.parse(MockResponseInfo(status_code=404))


def test_pip_item_retry(pip_item: API):
    item_code = "11111111"
    is_combination = True
    t = EndpointTester(pip_item.get_item(item_code, is_combination))
    t.prepare()

    with pytest.raises(APIError):
        t.parse(MockResponseInfo(status_code=404))
