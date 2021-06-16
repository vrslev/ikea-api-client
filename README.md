# IKEA API Client

Manage cart, check available delivery options, lookup your purchase history.

## Features

### Cart

- add, delete and update items
- copy cart from another user
- set and delete coupon
- show
- clear

### Order Capture

- get available delivery services

### Purchase

- get history
- get order info (can be used without authorization by login)

### Get items specs

## Example

```python
from ikea_api import get_guest_token, Cart, OrderCapture

token = get_guest_token()
cart = Cart(token)
cart.add_items({'30457903': 1})
order_capture = OrderCapture(token, zip_code='101000')
services = order_capture.get_delivery_services()
print(services)
```

## Installation

```bash
pip install git+git://github.com/vrslev/ikea-api-client.git@master
```
