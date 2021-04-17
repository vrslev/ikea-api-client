from ikea_api import get_guest_token, Cart, OrderCapture

token = get_guest_token()
cart = Cart(token)
cart.add_items({'30457903': 1})
order_capture = OrderCapture(token, 'your_zip_code')
deliveries = order_capture.get_delivery_services()
print(deliveries)