from __future__ import annotations

import json
import re
from typing import Any

import pytest
import responses

from ikea_api._constants import Constants
from ikea_api._endpoints.stock_ingka import IngkaStock
from ikea_api.exceptions import IKEAAPIError


def add_response(json: dict[str, Any]):
    responses.add(
        method=responses.GET,
        url=re.compile(
            f"https://api.ingka.ikea.com/cia/availabilities/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}"
        ),
        json=json,
    )


@responses.activate
@pytest.mark.parametrize(
    "response",
    (
        {"errors": {}},
        {"errors": []},
        {
            "errors": [
                {
                    "code": 404,
                    "message": "Not found",
                    "details": [],
                }
            ]
        },
    ),
)
def test_ingka_stock_error_handler_raises_without_item_code(response: dict[str, Any]):
    add_response(response)
    with pytest.raises(IKEAAPIError) as exc:
        IngkaStock()(["111"])
    assert exc.value.args == ((200, json.dumps(response)),)


@responses.activate
def test_ingka_stock_error_handler_raises_with_item_code():
    response = {
        "availabilities": None,
        "errors": [
            {
                "code": 404,
                "message": "Not found",
                "details": {
                    "classUnitCode": "RU",
                    "classUnitType": "RU",
                    "itemNo": "11111111",
                },
            }
        ],
    }
    add_response(response)
    with pytest.raises(IKEAAPIError) as exc:
        IngkaStock()(["111"])
    assert exc.value.args == (["11111111"],)


@responses.activate
def test_ingka_stock_passes():
    response: dict[str, Any] = {"data": [{}]}
    add_response(response)

    item_codes = ["11111111", "22222222"]

    class MockIngkaStock(IngkaStock):
        def _get(
            self,
            endpoint: str | None = None,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
        ):
            assert params == {
                "itemNos": item_codes,
                "expand": "StoresList,Restocks,SalesLocations",
            }
            return super()._get(endpoint=endpoint, headers=headers, params=params)

    assert MockIngkaStock()(item_codes) == response
