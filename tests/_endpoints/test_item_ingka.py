import json
import re
from typing import Any

import pytest
import responses

from ikea_api._constants import Constants
from ikea_api._endpoints.item_ingka import IngkaItems
from ikea_api.exceptions import IkeaApiError


def add_response(json: dict[str, Any]):
    responses.add(
        method=responses.GET,
        url=re.compile(
            f"https://api.ingka.ikea.com/salesitem/communications/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}"
        ),
        json=json,
    )


@responses.activate
@pytest.mark.parametrize(
    "response",
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
def test_ingka_items_error_handler_raises_without_item_codes(response: dict[str, Any]):
    add_response(response)
    with pytest.raises(IkeaApiError) as exc:
        IngkaItems()(["111"])
    assert exc.value.args == ((200, json.dumps(response)),)


@responses.activate
def test_ingka_items_error_handler_raises_with_item_codes():
    response = {
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
    add_response(response)
    with pytest.raises(IkeaApiError) as exc:
        IngkaItems()(["111"])
    assert exc.value.args == (["11111111"],)


def test_ingka_items_raises_on_more_than_50_items():
    with pytest.raises(RuntimeError, match="Can't get more than 50 items at once"):
        IngkaItems()(["111"] * 51)


@responses.activate
@pytest.mark.parametrize("count", (20, 49, 50))
def test_ingka_items_passes(count: int):
    response: dict[str, Any] = {"data": [{}]}
    add_response(response)

    item_codes = ["11111111"] * count

    class MockIngkaItems(IngkaItems):
        def _get(
            self,
            endpoint: str | None = None,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
        ):
            assert params == {"itemNos": item_codes}
            return super()._get(endpoint=endpoint, headers=headers, params=params)

    assert MockIngkaItems()(item_codes) == response
