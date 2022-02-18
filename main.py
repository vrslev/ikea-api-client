from new.constants import Constants
from new.endpoints import auth, cart
from new.executors.requests import RequestsExecutor, run
from new.wrappers import add_items_to_cart

item = "29429732"
token = run(auth.API(Constants()).get_guest_token())
cart_ = cart.API(Constants(), token=token)
wrapper = add_items_to_cart(cart_, {item: 1})
print(RequestsExecutor.run_wrapper(wrapper))
# print(run(pip_item.API(Constants()).get_item(item)))
