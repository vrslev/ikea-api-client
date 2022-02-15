from new.abc import BaseAPI, Endpoint, RequestInfo, SessionInfo, add_handler
from new.error_handlers import handle_json_decode_error


class API(BaseAPI):
    def get_session_info(self) -> SessionInfo:
        url = "https://api.ingka.ikea.com/guest/token"
        headers = self.extend_default_headers(
            {
                "Accept": "*/*",
                "Accept-Language": "en-us",
                "X-Client-Id": "e026b58d-dd69-425f-a67f-1e9a5087b87b",
                "X-Client-Secret": "cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB",
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @add_handler(handle_json_decode_error)
    def get_guest_token(self) -> Endpoint[str]:
        response = yield RequestInfo(
            "POST", "", json={"retailUnit": self.const.country}
        )
        return response.json["access_token"]
