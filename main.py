import sys
from typing import Any

from ikea_api._endpoints.auth import get_guest_token
from new import run
from new.abc import Endpoint
from new.constants import Constants
from new.endpoints import cart, pip_item, purchases
from new.exceptions import GraphQLError
from new.wrappers import get_purchase_history

token = get_guest_token()


def my_method() -> Endpoint[Any]:
    constants = Constants()
    try:
        yield from purchases.API(constants, token="token").history()
        print("OK?")
    except GraphQLError:
        pass
    val = yield from cart.API(constants, token=token).show()
    return val


# print(run(get_purchase_history(Constants(), "test")))
print(run(my_method()))

# print(run(pip_item.API(Constants()).get_item("40277973")))
