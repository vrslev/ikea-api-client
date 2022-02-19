from ikea_api.abc import BaseAPI, Endpoint, ResponseInfo, SessionInfo, endpoint
from ikea_api.constants import Constants
from tests.conftest import EndpointTester, MockResponseInfo


def test_error_handlers(constants: Constants):
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

    t = EndpointTester(API(constants).get_something("somecoolthing"))
    resp = t.parse(MockResponseInfo(json_={"onlysomethng": "tada"}), handle_errors=True)
    assert resp == "You're welcome!"
