import pytest
import requests
import responses

from ikea_api._endpoints.item_pip import PipItem
from ikea_api.exceptions import IkeaApiError


def test_item_pip_init():
    pip_item = PipItem()
    assert pip_item.endpoint == f"https://www.ikea.com/ru/ru/products"
    assert pip_item._session.headers["Accept"] == "*/*"


@pytest.mark.parametrize(
    "is_combintaion,exp_url",
    ((True, "/111/s11111111.json"), (False, "/111/11111111.json")),
)
@responses.activate
def test_item_pip_request_item(is_combintaion: bool, exp_url: str):
    pip_item = PipItem()
    item_code = "11111111"
    responses.add(responses.GET, url=f"{pip_item.endpoint}{exp_url}", json={})
    assert pip_item._request_item(item_code, is_combintaion) == {}


def test_item_pip_call_ok_first_time():
    exp_item_code = "1111111"
    called_request_item = False

    class MockPipItem(PipItem):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            called_request_item = True
            assert is_combination
            assert item_code == exp_item_code

    MockPipItem()(exp_item_code)
    assert called_request_item


def test_item_pip_call_ok_second_time():
    exp_item_code = "1111111"
    called_request_item = False
    exp_response = {"valid": "response"}

    class MockPipItem(PipItem):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            assert item_code == exp_item_code
            if called_request_item:
                assert not is_combination
                return exp_response
            else:
                assert is_combination
                called_request_item = True
                response = requests.Response()
                response.status_code = 404
                response._content = b"some msg"
                raise IkeaApiError(response)

    assert MockPipItem()(exp_item_code) == exp_response
    assert called_request_item


@pytest.mark.parametrize("exp_status", (404, 403))
def test_item_pip_call_not_ok(exp_status: int):
    exp_item_code = "1111111"
    called_request_item = False
    exp_msg = "some msg"

    class MockPipItem(PipItem):
        def _request_item(self, item_code: str, is_combination: bool):
            nonlocal called_request_item
            assert item_code == exp_item_code
            if called_request_item:
                assert not is_combination
            else:
                assert is_combination
                called_request_item = True
            response = requests.Response()
            response.status_code = exp_status
            response._content = exp_msg.encode()
            raise IkeaApiError(response)

    with pytest.raises(IkeaApiError) as exc:
        MockPipItem()(exp_item_code)
    assert exc.value.args == ((exp_status, exp_msg),)
    assert called_request_item
