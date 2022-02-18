import asyncio

from new.constants import Constants
from new.endpoints import auth, cart, ingka_items
from new.executors.requests import run
from new.wrappers import add_items_to_cart, get_items

items = ["29429732"]
# https://api.ingka.ikea.com/salesitem/communications/ru/ru/?itemNos=29429732
# https://api.ingka.ikea.com/salesitem/communications/ru/ru?itemNos=29429732
run(ingka_items.API(Constants()).get_items(items))
# asyncio.run(get_items(Constants(), items))
# item = "29429732"
# token = run(auth.API(Constants()).get_guest_token())
# cart_ = cart.API(Constants(), token=token)
# wrapper = add_items_to_cart(cart_, {item: 1})
# # print(run(pip_item.API(Constants()).get_item(item)))
