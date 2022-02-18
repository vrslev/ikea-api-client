from typing import Any

from new.abc import (
    BaseAPI,
    EndpointGen,
    RequestInfo,
    ResponseInfo,
    SessionInfo,
    add_handler,
)
from new.constants import Constants
from tests.new.conftest import EndpointTester, MockResponseInfo


def test_error_handlers(constants: Constants):
    def handle_no_anotherthing(response: ResponseInfo[Any]) -> None:
        try:
            response.json["anotherthing"]
        except KeyError:
            response.json["anotherthing"] = "You're welcome!"

    class Something:
        pass

    class API(BaseAPI):
        def get_session_info(self) -> SessionInfo:
            return SessionInfo("", {})

        @add_handler(handle_no_anotherthing)
        def get_something(self, something: str) -> EndpointGen[Something]:
            response = yield RequestInfo("POST", "", json={"name": something})
            return response.json["anotherthing"]

    t = EndpointTester(API(constants).get_something("somecoolthing"))
    resp = t.parse(MockResponseInfo(json_={"onlysomethng": "tada"}))
    assert resp == "You're welcome!"
