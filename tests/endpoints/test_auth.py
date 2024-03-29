from ikea_api.constants import Constants
from ikea_api.endpoints.auth import Auth
from tests.conftest import EndpointTester, MockResponseInfo


def test_get_guest_token(constants: Constants):
    c = EndpointTester(Auth(constants).get_guest_token())

    request_info = c.prepare()
    assert request_info.json == {"retailUnit": constants.country}

    token = "mytoken"  # nosec
    assert c.parse(MockResponseInfo(json_={"access_token": token})) == token
