from new.constants import Constants
from new.core import run
from new.endpoints import pip_item

api = pip_item.API(Constants())
res = run(api.get_item("89128566"))
print(res)
