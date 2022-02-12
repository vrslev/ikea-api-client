from new.constants import Constants
from new.endpoints.item_ingka import IngkaItemsAPI, IngkaItemsData
from new.executors import requests_executor

api = IngkaItemsAPI(Constants())
data = IngkaItemsData(["30457903"])
res = requests_executor(api.get_items, data)
print(res)
