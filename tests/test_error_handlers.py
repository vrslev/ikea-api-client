from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.error_handlers import (
    handle_401,
    handle_graphql_error,
    handle_json_decode_error,
    handle_not_success,
)
from ikea_api.exceptions import AuthError, GraphQLError, JSONError, NotSuccessError
from ikea_api.executors.requests import RequestsResponseInfo
from tests.conftest import MockResponseInfo


def test_handle_json_decode_error():
    response = MockResponseInfo()
    with pytest.raises(JSONError):
        handle_json_decode_error(response)


def test_handle_401():
    response = MockResponseInfo(status_code=401)
    with pytest.raises(AuthError):
        handle_401(response)


def test_handle_not_success():
    req_response: Any = SimpleNamespace(
        status_code=500, headers={}, ok=False, text=None
    )
    response = RequestsResponseInfo(req_response)
    with pytest.raises(NotSuccessError):
        handle_not_success(response)


@pytest.mark.parametrize(
    ("response", "expected"),
    (
        ({"errors": ["myerror"]}, ["myerror"]),
        (
            [
                {"errors": ["error1"]},
                {"errors": ["error2"]},
                {"response": "something"},
                {"response": ["something"]},
            ],
            ["error1", "error2"],
        ),
    ),
)
def test_handle_graphql_error(response: Any, expected: Any):
    response = MockResponseInfo(json_=response)
    with pytest.raises(GraphQLError) as exc:
        handle_graphql_error(response)

    assert exc.value.errors == expected
