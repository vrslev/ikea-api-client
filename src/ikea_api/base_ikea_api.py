from __future__ import annotations

from ikea_api.abc import BaseAPI
from ikea_api.constants import Constants, get_default_headers


class BaseIkeaAPI(BaseAPI):
    _const: Constants

    def __init__(self, constants: Constants) -> None:
        self._const = constants
        super().__init__()

    def _extend_default_headers(self, headers: dict[str, str]) -> dict[str, str]:
        res = get_default_headers(constants=self._const).copy()
        res.update(headers)
        return res


class BaseAuthIkeaAPI(BaseIkeaAPI):
    token: str

    def __init__(self, constants: Constants, *, token: str) -> None:
        self.token = token
        super().__init__(constants)

    def _extend_default_headers_with_auth(
        self, headers: dict[str, str]
    ) -> dict[str, str]:
        res = super()._extend_default_headers(headers)
        res["Authorization"] = "Bearer " + self.token
        return res
