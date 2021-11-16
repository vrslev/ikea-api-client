import json

import pytest
import requests
import responses
from responses.matchers import header_matcher, json_params_matcher

from ikea_api._constants import DEFAULT_HEADERS, Constants, Secrets
from ikea_api._endpoints.auth import get_guest_token

mock_guest_token_response = {
    "access_token": "random_token",
    "expires_in": "720h",
    "token_type": "Bearer",
}


@responses.activate
def test_get_guest_token_passes():
    responses.add(
        responses.POST,
        "https://api.ingka.ikea.com/guest/token",
        json=mock_guest_token_response,
        match=[
            header_matcher(
                {
                    **DEFAULT_HEADERS,
                    "Accept": "*/*",
                    "Accept-Language": "en-us",
                    "X-Client-Id": Secrets.auth_guest_token_x_client_id,
                    "X-Client-Secret": Secrets.auth_guest_token_x_client_secret,
                }
            ),
            json_params_matcher({"retailUnit": Constants.COUNTRY_CODE}),
        ],
    )
    assert get_guest_token() == mock_guest_token_response["access_token"]


@responses.activate
def test_get_guest_token_failes():
    responses.add(
        responses.POST,
        "https://api.ingka.ikea.com/guest/token",
        json=mock_guest_token_response,
        status=403,
    )
    with pytest.raises(
        requests.exceptions.HTTPError, match=json.dumps(mock_guest_token_response)
    ):
        assert get_guest_token() == mock_guest_token_response["access_token"]
