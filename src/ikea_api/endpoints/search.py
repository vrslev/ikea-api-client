from typing import Any, Literal

from ikea_api.abc import Endpoint, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseIkeaAPI
from ikea_api.constants import get_default_headers
from ikea_api.error_handlers import handle_json_decode_error

SearchType = Literal["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]


class API(BaseIkeaAPI):
    def get_session_info(self) -> SessionInfo:
        url = f"https://sik.search.blue.cdtapps.com/{self.const.country}/{self.const.language}/search-result-page"
        return SessionInfo(base_url=url, headers=get_default_headers(self.const))

    @endpoint(handlers=[handle_json_decode_error])
    def search(
        self,
        query: str,
        *,
        limit: int = 24,
        types: list[SearchType] = ["PRODUCT"],
    ) -> Endpoint[dict[str, Any]]:
        params = {
            "autocorrect": "true",
            "subcategories-style": "tree-navigation",
            "types": ",".join(types),
            "q": query,
            "size": limit,
            "c": "sr",  # API client: sr - search results, sb - search bar
            "v": "20210322",  # API version
        }
        response = yield self.RequestInfo("GET", params=params)
        return response.json
