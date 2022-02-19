from ikea_api.abc import BaseAPI
from ikea_api.constants import Constants, get_default_headers


class BaseIkeaAPI(BaseAPI):
    const: Constants

    def __init__(self, constants: Constants) -> None:
        self.const = constants
        super().__init__()

    def extend_default_headers(self, headers: dict[str, str]) -> dict[str, str]:
        res = get_default_headers(constants=self.const)
        res.update(headers)
        return res
