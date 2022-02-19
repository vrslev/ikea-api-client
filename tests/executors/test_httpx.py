from typing import cast

import httpx
import pytest

import ikea_api.executors.httpx
from ikea_api.abc import SessionInfo
from ikea_api.executors.httpx import HttpxResponseInfo, get_session_from_info, run
from tests.conftest import ExecutorContext


def test_httpx_response_info():
    headers = {"Accept": "*/*"}
    status_code = 200
    text = '{"ok":"ok"}'
    json = {"ok": "ok"}
    response = httpx.Response(
        status_code=status_code, headers=headers, text=text, json=json
    )
    info = HttpxResponseInfo(response)
    assert info.headers == response.headers  # type: ignore
    assert info.status_code == response.status_code  # type: ignore
    assert info.text == response.text
    assert info.json == response.json()
    assert info.is_success == response.is_success


def test_httpx_get_session_from_info_same():
    headers = {"Accept": "*/*"}
    one = get_session_from_info(
        SessionInfo(base_url="https://example.com", headers=headers)
    )
    two = get_session_from_info(
        SessionInfo(base_url="https://not.example.com", headers=headers)
    )
    assert one is two


def test_httpx_get_session_from_info_not_same():
    one = get_session_from_info(SessionInfo("", headers={"Accept": "*/*"}))
    two = get_session_from_info(SessionInfo("", headers={"Accept": "application/json"}))
    assert one != two


async def test_httpx_executor(
    monkeypatch: pytest.MonkeyPatch, executor_context: ExecutorContext
):
    req = executor_context.request
    session = req.session_info

    def handler(request: httpx.Request):
        assert request.method == req.method  # type: ignore
        url = cast(httpx.URL, request.url)  # type: ignore
        assert url == f"{session.base_url}{req.url}?{url.params}"
        assert request.content.decode() == req.data
        headers = session.headers.copy()
        headers.update(req.headers)
        for key, value in headers.items():
            assert request.headers[key] == value  # type: ignore

        return httpx.Response(200, json=executor_context.response.json)

    def func(session_info: SessionInfo):
        assert session_info == session
        transport = httpx.MockTransport(handler)
        return httpx.AsyncClient(headers=session.headers, transport=transport)

    monkeypatch.setattr(ikea_api.executors.httpx, "get_session_from_info", func)
    await run(executor_context.func())
