import pytest
import responses

from ikea_api._endpoints.item_pip import ItemPip
from ikea_api.errors import IkeaApiError


def test_item_pip_init():
    assert ItemPip().endpoint == f"https://www.ikea.com/ru/ru/products"


@pytest.mark.parametrize(
    "is_combintaion,exp_url",
    ((True, "/111/s11111111.json"), (False, "/111/11111111.json")),
)
@responses.activate
def test_item_pip_request_item(is_combintaion: bool, exp_url: str):
    item_pip = ItemPip()
    item_code = "11111111"
    responses.add(responses.GET, url=f"{item_pip.endpoint}{exp_url}", json={})
    assert item_pip._request_item(item_code, is_combintaion) == {}


def test_item_pip_call_ok_first_time():
    exp_item_code = "1111111"
    called_request_item = False

    class MockItemPip(ItemPip):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            called_request_item = True
            assert is_combination
            assert item_code == exp_item_code

    MockItemPip()(exp_item_code)
    assert called_request_item


def test_item_pip_call_ok_second_time():
    exp_item_code = "1111111"
    called_request_item = False
    exp_response = {"valid": "response"}

    class MockItemPip(ItemPip):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            assert item_code == exp_item_code
            if called_request_item:
                assert not is_combination
                return exp_response
            else:
                assert is_combination
                called_request_item = True
                raise IkeaApiError(404, "some msg")

    assert MockItemPip()(exp_item_code) == exp_response
    assert called_request_item


def test_item_pip_call_not_ok():
    exp_item_code = "1111111"
    called_request_item = False
    exp_msg = "some msg"
    exp_status = 404

    class MockItemPip(ItemPip):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            assert item_code == exp_item_code
            if called_request_item:
                assert not is_combination
            else:
                assert is_combination
                called_request_item = True
            raise IkeaApiError(exp_status, exp_msg)

    with pytest.raises(IkeaApiError) as exc:
        MockItemPip()(exp_item_code)
    assert exc.value.args == (exp_status, exp_msg)
    assert called_request_item
