from new.constants import Constants
from new.endpoints.item_ingka import get_items
from new.executors.requests import run

print(run(get_items(["30457903"]), Constants()))
