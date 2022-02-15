from ikea_api._endpoints.auth import get_guest_token
from new import run
from new.constants import Constants
from new.endpoints import pip_item

print(run(pip_item.API(Constants()).get_item("40277973")))
