from ikea_api._endpoints.auth import get_guest_token
from new import run
from new.constants import Constants
from new.endpoints import cart, order_capture

token = get_guest_token()
cart_ = cart.API(Constants(), token=token)
run(cart_.add_items({"30457903": 1}))
cart_response = run(cart_.show())
op = order_capture.API(Constants(), token=token)
checkout_id = run(
    op._get_checkout(order_capture.convert_cart_to_checkout_items(cart_response))
)
service_area_id = run(op._get_service_area(checkout_id, "101000"))
res = op.get_home_delivery_services(checkout_id, service_area_id)
print(run(res))
