from ikea_api._endpoints.auth import get_guest_token
from new import run
from new.constants import Constants
from new.endpoints import pip_item
from new.wrappers import get_purchase_history

print(run(get_purchase_history(Constants(), "test")))

# print(run(pip_item.API(Constants()).get_item("40277973")))
