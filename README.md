Client for several IKEA APIs.

[![License](https://img.shields.io/pypi/l/ikea_api?color=green)](https://github.com/vrslev/ikea-api-client/blob/master/LICENSE)
[![Version](https://img.shields.io/pypi/v/ikea_api?color=green&label=version)](https://pypi.org/project/ikea_api/)
[![Python Version](https://img.shields.io/pypi/pyversions/ikea_api?color=green)](https://pypi.org/project/ikea_api/)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?color=green)](https://pypi.org/project/ikea_api/)

# Features

-   Authorization (as guest or as user)
-   Cart managing
-   Available Delivery Services checking
-   Purchase History and specific Purchase Info getting
-   Item Info fetching

# Installation

This package requires Python >=3.7

```bash
python3 -m pip install ikea_api
```

This project uses [Flit](https://github.com/takluyver/flit) for distribution. To install it locally (for development) do this:

```bash
python3 -m pip install flit
git clone https://github.com/vrslev/ikea-api-client
cd ikea-api-client
flit install
```

# Endpoints

## [Authorization](https://github.com/vrslev/ikea-api-client/blob/master/ikea_api/auth.py)

### [Get Guest Token](https://github.com/vrslev/ikea-api-client/blob/f466ccc2e77a44cf9d87c0ffeab109e51690c491/ikea_api/auth.py#L19-L19)

```python
from ikea_api import get_guest_token
token = get_guest_token()
```

First time you open IKEA.com guest token is being generated and stored in Cookies. It expires in 30 days.

### [Get Authorized Token](https://github.com/vrslev/ikea-api-client/blob/f466ccc2e77a44cf9d87c0ffeab109e51690c491/ikea_api/auth.py#L46-L46)

IKEA uses OAuth2 to authorize their users. It lasts 1 day.

```python
from ikea_api import get_authorized_token
token = get_authorized_token('username', 'password')
```

## [Cart](https://github.com/vrslev/ikea-api-client/blob/master/ikea_api/endpoints/cart/__init__.py)

This API endpoint allows you to do everything you would be able to do on the site, and even more:

-   Add, Delete and Update items
-   Show cart
-   Clear cart
-   Set and Delete Coupon
-   Copy cart from another user

Works with and without authorization. If you logged in all changes apply to the _real_ cart. Use case: programmatically add items to cart and order it manually on IKEA.com.

Example:

```python
from ikea_api import Cart

token = ...
cart = Cart(token)
cart.add_items({'30457903': 1})
print(cart.show())
```

## [Order Capture](https://github.com/vrslev/ikea-api-client/blob/master/ikea_api/endpoints/order_capture/__init__.py)

Check availability for Pickup or Delivery. This is the only way.

If you need to know whether items are available in stores, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

```python
from ikea_api import Cart, OrderCapture

token = ...

cart = Cart(token)
cart.add_items({"30457903": 1})

order_capture = OrderCapture(token, zip_code="101000")
services = order_capture.get_delivery_services()
print(services)
```

## [Purchases](https://github.com/vrslev/ikea-api-client/blob/master/ikea_api/endpoints/purchases/__init__.py)

### [Order History](https://github.com/vrslev/ikea-api-client/blob/f466ccc2e77a44cf9d87c0ffeab109e51690c491/ikea_api/endpoints/purchases/__init__.py#L31-L31)

```python
from ikea_api import Purchases

authorized_token = ...

purchases = Purchases(authorized_token)
print(purchases.history())
```

### [Order Info](https://github.com/vrslev/ikea-api-client/blob/f466ccc2e77a44cf9d87c0ffeab109e51690c491/ikea_api/endpoints/purchases/__init__.py#L41-L41)

```python
from ikea_api import Purchases

order_number = ...

authorized_token = ...
purchases = Purchases(authorized_token)
order = purchases.order_info(order_number)

# Or use it without authorization, email is required
guest_token = ...
purchases = Purchases(guest_token)
order = purchases.order_info(order_number, email="email@example.com")

print(order)
```

## [Item Specs](https://github.com/vrslev/ikea-api-client/tree/master/ikea_api/endpoints/item)

Get information about item by item number

```python
from ikea_api import fetch_items_specs

item_codes = ["30457903"]

items = fetch_items_specs.iows(item_codes)

# or
items = fetch_items_specs.ingka(item_codes)

# or
item_codes_dict = {d: True for d in items} # True — is SPR i. e. combination
items = fetch_items_specs.pip(item_codes_dict)
```

There are many ways because information about some items is not available in some endpoints.

# [Response Examples](https://github.com/vrslev/ikea-api-client/tree/master/response_examples)

You can review response examples for all endpoint before using it [here](https://github.com/vrslev/ikea-api-client/tree/master/response_examples)
