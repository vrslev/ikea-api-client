import json
import sys

import pytest
import requests
import responses

from ikea_api._api import API, AuthorizedAPI, GraphQLAPI
from ikea_api._constants import DEFAULT_HEADERS
from ikea_api.exceptions import GraphQLError, IkeaApiError, UnauthorizedError
from ikea_api.types import CustomResponse

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


@pytest.fixture
def api():
    return API("https://example.com")


def test_api_init_endpoint():
    assert API("test").endpoint == "test"


def test_api_basic_error_handler_raises(api: API):
    response = CustomResponse()
    response.status_code = 401
    response._json = {}
    with pytest.raises(UnauthorizedError, match=str(response._json)):
        api._basic_error_handler(response)


def test_api_basic_error_handler_passes(api: API):
    response = CustomResponse()
    response.status_code = 400
    response._json = {}
    api._basic_error_handler(response)


def test_api_init_headers(api: API):
    exp_headers = requests.Session().headers
    exp_headers.update(DEFAULT_HEADERS)
    assert api._session.headers == exp_headers


@responses.activate
def test_api_request_endpoint_not_set(api: API):
    response = {"test": "test"}
    responses.add(responses.POST, api.endpoint, json=response)
    assert api._post() == response


@pytest.mark.parametrize("method", ("GET", "POST"))
@responses.activate
def test_api_request_methods_pass(api: API, method: Literal["GET", "POST"]):
    # TODO: Check if headers and data passed
    response = {"test": "test"}
    responses.add(method, api.endpoint, json=response)
    func = api._get if method == "GET" else api._post
    assert func() == response


@responses.activate
def test_api_request_method_not_json(api: API):
    response = "test"
    responses.add(responses.POST, api.endpoint, body=response)
    with pytest.raises(IkeaApiError) as exc:
        api._post()
    assert exc.value.args == ((200, response),)


@responses.activate
def test_api_request_error_handlers_called():
    exp_response = {"test": "test"}
    called_basic_error_handler = False
    called_error_handler = False

    class MockAPI(API):
        def _basic_error_handler(self, response: CustomResponse):
            assert response.status_code == 200
            assert response._json == exp_response
            nonlocal called_basic_error_handler
            called_basic_error_handler = True

        def _error_handler(self, response: CustomResponse):
            assert response.status_code == 200
            assert response._json == exp_response
            nonlocal called_error_handler
            called_error_handler = True

    api = MockAPI("https://example.com")
    responses.add(responses.POST, api.endpoint, json=exp_response)
    api._post()

    assert called_basic_error_handler
    assert called_error_handler


@responses.activate
def test_api_request_method_not_ok(api: API):
    response = {"test": "test"}
    status = 404
    responses.add(responses.POST, api.endpoint, json=response, status=status)
    with pytest.raises(IkeaApiError) as exc:
        api._post()
    assert exc.value.args == ((status, json.dumps(response)),)


def test_authorized_api_init():
    token = "some token"  # nosec
    api = AuthorizedAPI("", token)
    assert api._session.headers["Authorization"] == "Bearer " + token


def test_authorized_api_token_property_raises():
    api = AuthorizedAPI(endpoint="", token=None)
    with pytest.raises(RuntimeError, match="No token provided"):
        api.token


def test_authorized_token_property_not_raises():
    token = "some token"  # nosec
    api = AuthorizedAPI("", token)
    assert api.token == token


def test_graphql_api_basic_error_handler_graphqlerror():
    api = GraphQLAPI("https://example.com", "some token")
    response = CustomResponse()
    response.status_code = 200
    response._json = {"errors": None}
    with pytest.raises(GraphQLError, match=str(response._json)):
        api._basic_error_handler(response)
