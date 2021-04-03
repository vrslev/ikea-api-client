from ikea_api import get_guest_token, Cart

token = get_guest_token()
cart = Cart(token)
cart.add_items({'30457903': 1})
deliveries = cart.get_delivery_options('your_zip_code')
print(deliveries)