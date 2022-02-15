from __future__ import annotations

from typing import Any

import pytest
import responses

import new.utils
from new.utils import (
    _get_unshortened_links_from_ingka_pagelinks,
    format_item_code,
    parse_item_codes,
)


@responses.activate
@pytest.mark.parametrize(
    "v",
    (
        "https://www.ikea.com/ru/ru/p/fejka-feyka-iskusstvennoe-rastenie-v-gorshke-3sht-d-doma-ulicy-zelenyy-10485209/",
        "10485209",
    ),
)
def test_get_unshortened_links_from_ingka_pagelinks_no_value(v: str):
    _get_unshortened_links_from_ingka_pagelinks(v)


@responses.activate
def test_get_unshortened_links_from_ingka_pagelinks_with_value():
    pagelink = "https://ingka.page.link/Re4Cos2tqLvuf6Mz7"
    exp_url = (
        "https://www.ikea.com/ru/ru/p/fejka-feyka-iskusstvennoe-rastenie"
        + "-v-gorshke-3sht-d-doma-ulicy-zelenyy-10485209/"
    )
    responses.add(responses.GET, pagelink, headers={"Location": exp_url})

    assert list(_get_unshortened_links_from_ingka_pagelinks(pagelink)) == [exp_url]


def test_parse_item_codes_unshorten_ingka_pagelinks_false(
    monkeypatch: pytest.MonkeyPatch,
):
    called = False

    def mock_unshorten(v: str):
        nonlocal called
        called = True  # pragma: no cover

    monkeypatch.setattr(
        new.utils, "_get_unshortened_links_from_ingka_pagelinks", mock_unshorten
    )
    parse_item_codes([], unshorten_ingka_pagelinks=False)
    parse_item_codes([])
    assert not called


def test_parse_item_codes_unshorten_ingka_pagelinks_true_no_value(
    monkeypatch: pytest.MonkeyPatch,
):
    exp_val = "22222222"
    called = False

    def mock_unshorten(v: str):
        assert v == exp_val
        nonlocal called
        called = True

    monkeypatch.setattr(
        new.utils, "_get_unshortened_links_from_ingka_pagelinks", mock_unshorten
    )
    assert parse_item_codes(exp_val, unshorten_ingka_pagelinks=True) == [exp_val]
    assert called


@pytest.mark.parametrize("is_list", (True, False))
def test_parse_item_codes_unshorten_ingka_pagelinks_true(
    monkeypatch: pytest.MonkeyPatch, is_list: bool
):
    exp_val = "22222222"
    called = False

    def mock_unshorten(v: str):
        assert v == exp_val
        nonlocal called
        called = True
        yield "11111111"

    monkeypatch.setattr(
        new.utils, "_get_unshortened_links_from_ingka_pagelinks", mock_unshorten
    )

    if is_list:
        res = parse_item_codes([exp_val], unshorten_ingka_pagelinks=True)
    else:
        res = parse_item_codes(exp_val, unshorten_ingka_pagelinks=True)

    assert called
    assert res == [exp_val, "11111111"]


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


@pytest.mark.parametrize("v", (True, False))
def test_parse_item_codes_empty(v: bool):
    assert parse_item_codes([], unshorten_ingka_pagelinks=v) == []


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

    monkeypatch.setattr(new.utils, "parse_item_codes", mock_parse)
    assert format_item_code(input) == output
    assert called
