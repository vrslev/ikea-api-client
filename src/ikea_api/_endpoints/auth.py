import requests

from ikea_api._constants import DEFAULT_HEADERS, Constants, Secrets


def get_guest_token() -> str:
    resp = requests.post(
        url="https://api.ingka.ikea.com/guest/token",
        headers={
            **DEFAULT_HEADERS,
            "Accept": "*/*",
            "Accept-Language": "en-us",
            "X-Client-Id": Secrets.auth_guest_token_x_client_id,
            "X-Client-Secret": Secrets.auth_guest_token_x_client_secret,
        },
        json={"retailUnit": Constants.COUNTRY_CODE},
    )
    resp.reason = resp.text
    resp.raise_for_status()
    return resp.json()["access_token"]
