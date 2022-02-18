from typing import Any, Literal

from new.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from new.constants import get_default_headers
from new.error_handlers import handle_json_decode_error

SearchType = Literal["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]


class API(BaseAPI):
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
    ) -> EndpointGen[dict[str, Any]]:
        response = yield self.RequestInfo(
            method="GET",
            url="",
            params={
                "autocorrect": "true",
                "subcategories-style": "tree-navigation",
                "types": ",".join(types),
                "q": query,
                "size": limit,
                "c": "sr",  # API client: sr - search results, sb - search bar
                "v": "20210322",  # API version
            },
        )
        return response.json
