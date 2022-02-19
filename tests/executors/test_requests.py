from __future__ import annotations

import sys
from typing import Any

import pytest
import requests
from requests.structures import CaseInsensitiveDict

import ikea_api.executors.requests
from ikea_api.abc import SessionInfo
from ikea_api.executors.requests import (
    RequestsResponseInfo,
    get_cached_session,
    get_session_from_info,
    run,
)
from tests.conftest import ExecutorContext


def test_requests_import_fails():
    sys.modules["requests"] = None  # type: ignore
    with pytest.raises(RuntimeError, match="To use requests executor"):
        get_cached_session(headers=frozenset())  # type: ignore
    del sys.modules["requests"]


def test_requests_response_info():
    requests.Session()
    response = requests.Response()
    response.status_code = 200
    response.headers = CaseInsensitiveDict({"Accept": "*/*"})
    response._content = b'{"ok": "ok"}'

    info = RequestsResponseInfo(response)
    assert info.headers == response.headers
    assert info.status_code == response.status_code
    assert info.text == response.text
    assert info.json == response.json()
    assert info.is_success == response.ok


def test_requests_get_session_from_info_same():
    headers = {"Accept": "*/*"}
    one = get_session_from_info(
        SessionInfo(base_url="https://example.com", headers=headers)
    )
    two = get_session_from_info(
        SessionInfo(base_url="https://not.example.com", headers=headers)
    )
    assert one is two


def test_requests_get_session_from_info_not_same():
    one = get_session_from_info(SessionInfo("", headers={"Accept": "*/*"}))
    two = get_session_from_info(SessionInfo("", headers={"Accept": "application/json"}))
    assert one != two


def test_requests_executor(
    monkeypatch: pytest.MonkeyPatch, executor_context: ExecutorContext
):
    req = executor_context.request
    session = req.session_info
    resp = executor_context.response

    class CustomSession(requests.Session):
        def request(  # type: ignore
            self,
            method: str,
            url: str,
            params: dict[str, Any],
            data: Any,
            json: Any,
            headers: dict[str, str],
        ) -> requests.Response:
            assert method == req.method
            assert url == session.base_url + req.url
            assert params == req.params
            assert data == req.data
            assert json == req.json
            assert headers == req.headers

            response = requests.Response()
            response.status_code = resp.status_code
            response.headers == resp.headers
            response._content = resp.text.encode()
            return response

    def func(session_info: SessionInfo):
        assert session_info == session
        res = CustomSession()
        res.headers.update(session_info.headers)
        return res

    monkeypatch.setattr(ikea_api.executors.requests, "get_session_from_info", func)
    run(executor_context.func())
