from new.constants import Constants
from new.endpoints.ingka_items import API, Data
from new.executors import requests_executor

api = API(Constants())
data = Data(["30457903"])
res = requests_executor(api.get_items, data)
print(res)
