import json
import sys
from copy import copy
from typing import Any

import pytest
import responses

from ikea_api._endpoints.purchases import Purchases, Queries
from ikea_api.exceptions import GraphQLError

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


@pytest.fixture
def purchases():
    return Purchases("mytoken")


def test_build_payload(purchases: Purchases):
    assert purchases._build_payload("myoperation", "myquery", var1=1, var2=2) == {
        "operationName": "myoperation",
        "variables": {"var1": 1, "var2": 2},
        "query": "myquery",
    }


def get_headers():
    return {
        "Accept": "*/*",
        "Accept-Language": "ru-ru",
        "Origin": "https://order.ikea.com",
        "Referer": "https://order.ikea.com/ru/ru/purchases/",
    }


@responses.activate
def test_history_passes(purchases: Purchases):
    responses.add(
        responses.POST,
        purchases.endpoint,
        json={"foo": "bar"},
        match=[
            responses.matchers.json_params_matcher(  # type: ignore
                {
                    "operationName": "History",
                    "variables": {"take": 3, "skip": 2},
                    "query": Queries.history,
                }
            ),
            responses.matchers.header_matcher(get_headers()),  # type: ignore
        ],
    )
    assert purchases.history(take=3, skip=2) == {"foo": "bar"}


@responses.activate
def test_history_raises(purchases: Purchases):
    responses.add(
        responses.POST,
        purchases.endpoint,
        json={"errors": "foo"},
        match=[
            responses.matchers.json_params_matcher(  # type: ignore
                {
                    "operationName": "History",
                    "variables": {"take": 3, "skip": 2},
                    "query": Queries.history,
                }
            ),
            responses.matchers.header_matcher(get_headers()),  # type: ignore
        ],
    )
    with pytest.raises(GraphQLError, match="foo") as exc:
        purchases.history(take=3, skip=2)
    assert exc.value.errors == "foo"


@responses.activate
@pytest.mark.parametrize("status_banner", (True, False))
@pytest.mark.parametrize("costs", (True, False))
@pytest.mark.parametrize("product_list", (True, False))
@pytest.mark.parametrize("email", ("me@example.com", None))
def test_order_info_passes(
    purchases: Purchases,
    status_banner: bool,
    costs: bool,
    product_list: bool,
    email: str | None,
):
    payload: list[dict[str, Any]] = []
    queries: list[Literal["StatusBannerOrder", "CostsOrder", "ProductListOrder"]] = []
    order_number = "111111111"
    skip_products = 15
    skip_product_prices = True
    take_products = 25
    if status_banner:
        payload.append(
            {
                "operationName": "StatusBannerOrder",
                "variables": {"orderNumber": order_number},
                "query": Queries.status_banner_order,
            }
        )
        queries.append("StatusBannerOrder")
    if costs:
        payload.append(
            {
                "operationName": "CostsOrder",
                "variables": {"orderNumber": order_number},
                "query": Queries.costs_order,
            }
        )
        queries.append("CostsOrder")
    if product_list:
        payload.append(
            {
                "operationName": "ProductListOrder",
                "variables": {
                    "orderNumber": order_number,
                    "receiptNumber": "",
                    "skip": skip_products,
                    "skipPrice": skip_product_prices,
                    "take": take_products,
                },
                "query": Queries.product_list_order,
            }
        )
        queries.append("ProductListOrder")

    headers = get_headers()
    headers["Referer"] = f"{purchases._session.headers['Origin']}/{order_number}/"
    if email:
        headers["Referer"] = purchases._session.headers["Referer"] + "lookup"
        for chunk in payload:
            chunk["variables"]["liteId"] = email

    responses.add(
        responses.POST,
        purchases.endpoint,
        json=[{"foo": "bar"}],
        match=[responses.matchers.header_matcher(headers)],  # type: ignore
    )

    res = purchases.order_info(
        copy(order_number),
        email=copy(email),
        queries=queries,
        skip_products=copy(skip_products),
        skip_product_prices=copy(skip_product_prices),
        take_products=copy(take_products),
    )

    assert len(responses.calls) == 1
    assert json.loads(responses.calls[0].request.body) == payload  # type: ignore
    assert res == [{"foo": "bar"}]


@responses.activate
def test_order_info_raises(purchases: Purchases):
    responses.add(
        responses.POST,
        purchases.endpoint,
        json=[{"errors": "err1"}, {"errors": "err2"}],
    )
    with pytest.raises(GraphQLError, match="['err1', 'err2']") as exc:
        purchases.order_info("1")
    assert exc.value.errors == ["err1", "err2"]
