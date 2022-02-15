from new.constants import Constants
from new.core import run
from new.endpoints import item_pip

api = item_pip.API(Constants())
res = run(api.get_item("89128566"))
print(res)
