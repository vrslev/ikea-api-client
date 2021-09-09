from typing import Any

import pytest
import responses
from requests import Session

from ikea_api._api import API
from ikea_api.constants import DEFAULT_HEADERS
from ikea_api.errors import GraphQLError, UnauthorizedError


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
    responses.add(responses.POST, api._endpoint)
    api._request()
