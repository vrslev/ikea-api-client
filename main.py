from new.constants import Constants
from new.endpoints.ingka_items import API
from new.executors import requests_executor

api = API(Constants())
res = requests_executor(api.get_items(["30457903"]))
print(res)
