import json
from typing import Any

import pytest
import responses
from requests import Session
from typing_extensions import Literal

from ikea_api._api import API
from ikea_api.constants import DEFAULT_HEADERS
from ikea_api.errors import GraphQLError, IkeaApiError, UnauthorizedError


@pytest.fixture
def api():
    return API("some token", "https://example.com")


def test_api_init_token_endpoint():
    token, endpoint = "some token", "https://example.com"
    api = API(token, endpoint)
    assert api._API__token == token  # type: ignore
    assert api._endpoint == endpoint


def test_api_init_headers_without_token():
    api = API(None, "")
    exp_headers = Session().headers
    exp_headers.update(DEFAULT_HEADERS)
    assert api._session.headers == exp_headers


def test_api_init_headers_with_token():
    token = "some token"  # nosec
    api = API(token, "")
    exp_headers = Session().headers
    exp_headers.update(DEFAULT_HEADERS)
    exp_headers["Authorization"] = "Bearer " + token
    assert api._session.headers == exp_headers


def test_api_token_property_raises():
    api = API(None, "")
    with pytest.raises(RuntimeError, match="No token provided"):
        api._token


def test_api_token_property_not_raises():
    token = "some token"  # nosec
    api = API(token, "")
    assert api._token == token


def test_api_basic_error_handler_unauthorized(api: API):
    status_code = 401
    response: dict[Any, Any] = {}
    with pytest.raises(UnauthorizedError, match=str(response)):
        api._basic_error_handler(status_code, response)


def test_api_basic_error_handler_graphqlerror(api: API):
    status_code, response = 200, {"errors": None}
    with pytest.raises(GraphQLError, match=str(response)):
        api._basic_error_handler(status_code, response)


@responses.activate
def test_api_request_endpoint_not_set(api: API):
    response = {"test": "test"}
    responses.add(responses.POST, api._endpoint, json=response)
    assert api._request() == response


@pytest.mark.parametrize("method", ("GET", "POST"))
@responses.activate
def test_api_request_methods_pass(api: API, method: Literal["GET", "POST"]):
    response = {"test": "test"}
    responses.add(method, api._endpoint, json=response)
    assert api._request(method=method) == response


@responses.activate
def test_api_request_method_fail(api: API):
    response = {"test": "test"}
    method = "OPTIONS"
    responses.add(method, api._endpoint, json=response)
    with pytest.raises(RuntimeError, match=f'Unsupported method: "{method}"'):
        assert api._request(method=method) == response  # type: ignore


@responses.activate
def test_api_request_method_not_json(api: API):
    response = "test"
    responses.add(responses.POST, api._endpoint, body=response)
    with pytest.raises(IkeaApiError) as exc:
        api._request()
    assert exc.value.args == (200, response)


@responses.activate
def test_api_request_error_handlers_called():
    response = {"test": "test"}
    called_basic_error_handler = False
    called_error_handler = False

    class MockAPI(API):
        def _basic_error_handler(self, status_code: int, response: dict[Any, Any]):
            assert status_code == 200
            assert response == response
            nonlocal called_basic_error_handler
            called_basic_error_handler = True

        def _error_handler(self, status_code: int, response: dict[Any, Any]):  # type: ignore
            assert status_code == 200
            assert response == response
            nonlocal called_error_handler
            called_error_handler = True

    api = MockAPI("some token", "https://example.com")
    responses.add(responses.POST, api._endpoint, json=response)
    api._request()

    assert called_basic_error_handler
    assert called_error_handler


@responses.activate
def test_api_request_method_not_ok(api: API):
    response = {"test": "test"}
    status = 404
    responses.add(responses.POST, api._endpoint, json=response, status=status)
    with pytest.raises(IkeaApiError) as exc:
        api._request()
    assert exc.value.args == (status, json.dumps(response))
