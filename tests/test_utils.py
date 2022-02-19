from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import ikea_api.utils
from ikea_api.utils import (
    _get_location_headers,
    _parse_ingka_pagelink_urls,
    format_item_code,
    parse_item_codes,
)


def test_parse_item_codes_unique():
    assert parse_item_codes(["11111111", "1141211", "22222222", "11111111"]) == [
        "11111111",
        "22222222",
    ]


@pytest.mark.parametrize(
    "v",
    (
        "111.111.11",
        "111. 111. 11",
        "111 111,11",
        "111-111-11",
        "111111 11",
        "111,111,11",
    ),
)
def test_parse_item_codes_clean(v: str):
    assert parse_item_codes(v) == ["11111111"]


def test_parse_item_codes_empty():
    assert parse_item_codes([]) == []


page_link = "https://ingka.page.link/Re4Cos2tqLvuf6Mz7"


@pytest.mark.parametrize(
    ("v", "expected"),
    (
        (page_link, [page_link]),
        (
            f"text here {page_link} text there {page_link} text there",
            [page_link, page_link],
        ),
    ),
)
def test_parse_ingka_pagelink_urls(v: Any, expected: Any):
    assert list(_parse_ingka_pagelink_urls(v)) == expected


def test_get_location_headers():
    responses: tuple[Any, ...] = (
        SimpleNamespace(headers={"Location": "1"}),
        SimpleNamespace(headers={"Location": "2"}),
        SimpleNamespace(headers={}),
    )
    assert _get_location_headers(responses) == ["1", "2"]


@pytest.mark.parametrize(
    ("input", "output"),
    (
        ("111.111.11", "111.111.11"),
        ("111-111-11", "111.111.11"),
        ("11111111", "111.111.11"),
        ("", None),
        ("1111", None),
        ("111.111.1", None),
    ),
)
def test_format_item_code(
    monkeypatch: pytest.MonkeyPatch, input: str, output: str | None
):
    called = False

    def mock_parse(v: Any):
        nonlocal called
        called = True
        return parse_item_codes(v)

    monkeypatch.setattr(ikea_api.utils, "parse_item_codes", mock_parse)
    assert format_item_code(input) == output
    assert called
