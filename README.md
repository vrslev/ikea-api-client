# IKEA API Client

Manage cart, check available delivery options.
Note that all requests are made for Russian IKEA website. In future I'll add feature to change country. 

## Features
### Cart
- show
- clear
- add/delete items

### Order Capture
- get available delivery services

### Profile
- show purchase history
- show purchase info

### Fetch items specs

## Example
```python
from ikea_api import get_guest_token, Cart, OrderCapture

token = get_guest_token()
cart = Cart(token)
cart.add_items({'30457903': 1})
order_capture = OrderCapture(token, 'your_zip_code')
deliveries = order_capture.get_delivery_services()
print(deliveries)
```

## Installation
```
pip install git+git://github.com/vrslev/ikea-api-client.git@master
```