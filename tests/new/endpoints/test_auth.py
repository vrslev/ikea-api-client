from new.constants import Constants
from new.endpoints import auth
from tests.new.conftest import EndpointTester, MockResponseInfo


def test_get_guest_token(constants: Constants):
    c = EndpointTester(auth.API(constants).get_guest_token())

    request_info = c.prepare()
    assert request_info.json == {"retailUnit": constants.country}

    token = "mytoken"  # nosec
    assert c.parse(MockResponseInfo(json_={"access_token": token})) == token
