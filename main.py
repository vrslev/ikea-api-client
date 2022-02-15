from new.constants import Constants
from new.core import run
from new.endpoints.ingka_items import API

api = API(Constants())
res = run(api.get_items(["30457903"]))
print(res)
