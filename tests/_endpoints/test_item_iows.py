import re
from typing import Any

import pytest
import responses

from ikea_api._endpoints.item_iows import IowsItems
from ikea_api.exceptions import ItemFetchError


def test_set_initial_items():
    fetcher = IowsItems()
    fetcher._set_initial_items(["11111111", "22222222"])
    assert fetcher.items == {"11111111": False, "22222222": False}


def test_build_payload():
    items = {"11111111": False, "22222222": True, "33333333": True}
    assert IowsItems()._build_payload(items) == "ART,11111111;SPR,22222222;SPR,33333333"


def test_iows_items_raises_on_more_than_90_items():
    with pytest.raises(RuntimeError, match="Can't get more than 90 items at once"):
        IowsItems()(["111"] * 91)


@responses.activate
def test_iows_items_passes_one_item_first_time():
    fetcher = IowsItems()
    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,11111111",
        json={"RetailItemComm": "foo"},
    )

    assert fetcher(["11111111"]) == ["foo"]


@responses.activate
def test_iows_items_one_item_second_time():
    fetcher = IowsItems()
    responses.add(responses.GET, url=f"{fetcher.endpoint}ART,11111111", status=404)
    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}SPR,11111111",
        json={"RetailItemComm": "foo"},
    )

    assert fetcher(["11111111"]) == ["foo"]


@responses.activate
def test_iows_items_one_item_fails():
    fetcher = IowsItems()
    for url in (f"{fetcher.endpoint}ART,11111111", f"{fetcher.endpoint}SPR,11111111"):
        responses.add(
            responses.GET,
            url=url,
            json={"foo": None},
            status=404,
        )

    with pytest.raises(ItemFetchError, match="Wrong Item Code"):
        fetcher(["11111111"])


@pytest.mark.parametrize(
    "err",
    (
        [{"ErrorCode": {"$": 1100}}],
        {"ErrorCode": {"$": 1100}},
        {"ErrorCode": {}},
        {},
    ),
)
@responses.activate
def test_iows_items_multiple_fails(err: list[dict[str, Any]] | dict[str, Any]):
    fetcher = IowsItems()

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,11111111;ART,22222222",
        json={"ErrorList": {"Error": err}},
        status=403,
    )

    exp_msg = re.escape(str(err[0] if isinstance(err, list) else err))
    with pytest.raises(ItemFetchError, match=exp_msg):
        fetcher(["11111111", "22222222"])


@responses.activate
def test_iows_items_multiple_passes_first_time():
    fetcher = IowsItems()

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,11111111;ART,22222222;ART,33333333",
        json={"RetailItemCommList": {"RetailItemComm": ["foo", "bar", "op"]}},
    )

    assert fetcher(["11111111", "22222222", "33333333"]) == ["foo", "bar", "op"]


def build_item_error(**args: Any):
    prep_args = [{"Name": {"$": k}, "Value": {"$": v}} for k, v in args.items()]
    return {
        "ErrorCode": {"$": 1101},
        "ErrorAttributeList": {"ErrorAttribute": prep_args},
    }


def build_error(errors: list[dict[str, Any]]):
    return {"ErrorList": {"Error": errors}}


@responses.activate
def test_iows_items_multiple_passes_second_time():
    fetcher = IowsItems()

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,11111111;ART,22222222;ART,33333333",
        json=build_error(
            [
                build_item_error(ITEM_NO=11111111, ITEM_TYPE="ART"),
                build_item_error(ITEM_NO=33333333, ITEM_TYPE="ART"),
            ]
        ),
    )

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}SPR,11111111;ART,22222222;SPR,33333333",
        json={"RetailItemCommList": {"RetailItemComm": ["foo", "bar", "op"]}},
    )

    assert fetcher(["11111111", "22222222", "33333333"]) == ["foo", "bar", "op"]


@responses.activate
def test_iows_items_multiple_passes_third_time():
    fetcher = IowsItems()

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,11111111;ART,22222222;ART,33333333",
        json=build_error(
            [
                build_item_error(ITEM_NO=11111111, ITEM_TYPE="ART"),
                build_item_error(ITEM_NO=33333333, ITEM_TYPE="ART"),
            ]
        ),
    )

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}SPR,11111111;ART,22222222;SPR,33333333",
        json=build_error([build_item_error(ITEM_NO=11111111, ITEM_TYPE="SPR")]),
    )

    responses.add(
        responses.GET,
        url=f"{fetcher.endpoint}ART,22222222;SPR,33333333",
        json={"RetailItemCommList": {"RetailItemComm": ["foo", "bar"]}},
    )

    assert fetcher(["11111111", "22222222", "33333333"]) == ["foo", "bar"]
