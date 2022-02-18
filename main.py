from new.constants import Constants
from new.endpoints import auth, pip_item
from new.executors.requests import run

item = "29429732"
print(run(pip_item.API(Constants()).get_item(item)))
