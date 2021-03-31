from ikea_api.auth import Auth
from ikea_api.cart import Cart

token = Auth().get_authorized_token(username='username', password='password')
cart = Cart(token)
cart.add_items({'30457903': 1})
deliveries = cart.get_delivery_options('your_zip_code')
print(deliveries)