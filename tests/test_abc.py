from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from ikea_api.abc import (
    AsyncExecutor,
    BaseAPI,
    Endpoint,
    EndpointInfo,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    SyncExecutor,
    endpoint,
)
from tests.conftest import EndpointTester, MockResponseInfo


def test_endpoint_decorator():
    def handler(_: ResponseInfo) -> None:  # pragma: no cover
        ...

    def func() -> Endpoint[None]:  # pragma: no cover
        ...

    decorated_endpoint = endpoint(handlers=[handler])(func)
    info = decorated_endpoint()
    assert isinstance(info, EndpointInfo)
    assert info.func.func == func
    assert info.handlers == [handler]


def test_sync_executor():
    request_info = RequestInfo(
        SessionInfo("https://example.com", {}), "POST", "", params={}, headers={}
    )
    response_info = MockResponseInfo(json_="ok")

    class MyExecutor(SyncExecutor):
        @staticmethod
        def request(request: RequestInfo) -> MockResponseInfo:
            assert request == request_info
            return response_info

    mock = MagicMock()

    @endpoint(handlers=[mock])
    def myendpoint() -> Endpoint[tuple[str, str]]:
        response1 = yield request_info
        response2 = yield request_info
        return (response1.json, response2.json)

    assert MyExecutor.run(myendpoint()) == ("ok", "ok")
    mock.assert_called_with(response_info)


async def test_async_executor():
    request_info = RequestInfo(
        SessionInfo("https://example.com", {}), "POST", "", params={}, headers={}
    )
    response_info = MockResponseInfo(json_="ok")

    class MyExecutor(AsyncExecutor):
        @staticmethod
        async def request(request: RequestInfo) -> MockResponseInfo:
            assert request == request_info
            return response_info

    mock = MagicMock()

    @endpoint(handlers=[mock])
    def myendpoint() -> Endpoint[tuple[str, str]]:
        response1 = yield request_info
        response2 = yield request_info
        return (response1.json, response2.json)

    assert await MyExecutor.run(myendpoint()) == ("ok", "ok")
    mock.assert_called_with(response_info)


def test_error_handlers():
    def handle_no_anotherthing(response: ResponseInfo) -> None:
        try:
            response.json["anotherthing"]
        except KeyError:
            response.json["anotherthing"] = "You're welcome!"

    class Something:
        pass

    class API(BaseAPI):
        def get_session_info(self) -> SessionInfo:
            return SessionInfo("", {})

        @endpoint(handlers=[handle_no_anotherthing])
        def get_something(self, something: str) -> Endpoint[Something]:
            response = yield self.RequestInfo("POST", "", json={"name": something})
            return response.json["anotherthing"]

    t = EndpointTester(API().get_something("somecoolthing"))
    resp = t.parse(MockResponseInfo(json_={"onlysomethng": "tada"}), handle_errors=True)
    assert resp == "You're welcome!"


def test_base_api_request_info():
    session = SessionInfo("", {})
    mock_instance: Any = SimpleNamespace(session_info=session)
    res = BaseAPI.RequestInfo(
        mock_instance, "POST", url=None, params=None, headers=None, json=None, data=None
    )
    assert res == RequestInfo(
        session_info=session,
        method="POST",
        url="",
        params={},
        headers={},
        data=None,
        json=None,
    )
