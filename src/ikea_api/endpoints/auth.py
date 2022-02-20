from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.error_handlers import (
    handle_401,
    handle_json_decode_error,
    handle_not_success,
)


class Auth(BaseIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        url = "https://api.ingka.ikea.com/guest/token"
        headers = self._extend_default_headers(
            {
                "Accept": "*/*",
                "Accept-Language": "en-us",
                "X-Client-Id": "e026b58d-dd69-425f-a67f-1e9a5087b87b",
                "X-Client-Secret": "cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB",
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_json_decode_error, handle_401, handle_not_success])
    def get_guest_token(self) -> Endpoint[str]:
        response = yield self._RequestInfo(
            "POST", json={"retailUnit": self._const.country}
        )
        return response.json["access_token"]
