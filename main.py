import asyncio

from new.constants import Constants
from new.endpoints import auth, cart, ingka_items
from new.executors.requests import run
from new.wrappers.wrappers import add_items_to_cart, get_items

items = [
    "90458626",
    "70379569",
    "60497752",
    "20477633",
    "20371877",
    "10379497",
    "30467105",
    "30372329",
    "70382114",
    "60493344",
    "50360919",
    "20506485",
    "10350941",
    "60476349",
    "00519766",
    "80349548",
    "10485209",
    "29414151",
    "50443929",
    "50440959",
    "40367695",
    "10443926",
    "60444607",
    "20349669",
    "30372471",
    "60491571",
    "10429567",
    "70367694",
    "90375099",
    "70513407",
    "79278306",
    "70379574",
    "50375317",
    "20469157",
    "20368870",
    "10488057",
    "00488053",
    "30475394",
    "80485753",
    "90485757",
    "10485756",
    "60485754",
    "90446129",
    "80494615",
    "80409392",
    "80378244",
    "80377517",
    "80351013",
    "70501664",
    "70498992",
]
# https://api.ingka.ikea.com/salesitem/communications/ru/ru/?itemNos=29429732
# https://api.ingka.ikea.com/salesitem/communications/ru/ru?itemNos=29429732
# run(ingka_items.API(Constants()).get_items(items))
print(asyncio.run(get_items(Constants(), items)))
# item = "29429732"
# token = run(auth.API(Constants()).get_guest_token())
# cart_ = cart.API(Constants(), token=token)
# wrapper = add_items_to_cart(cart_, {item: 1})
# # print(run(pip_item.API(Constants()).get_item(item)))
