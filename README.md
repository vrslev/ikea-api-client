Client for several IKEA APIs.

[![License](https://img.shields.io/pypi/l/ikea_api?color=green)](https://github.com/vrslev/ikea-api-client/blob/master/LICENSE)
[![Version](https://img.shields.io/pypi/v/ikea_api?color=green&label=version)](https://pypi.org/project/ikea_api/)
[![Python Version](https://img.shields.io/pypi/pyversions/ikea_api?color=green)](https://pypi.org/project/ikea_api/)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?color=green)](https://pypi.org/project/ikea_api/)

# Features

- Authorization (as guest or as user)
- Manage Cart
- Check available Delivery Services
- Retrieve Purchases History and information about specific order
- Fetch Product information

# Installation

```bash
pip install ikea_api
```

If you are planning to use log in as registered user, you need to install Selenium and chromedriver:

```bash
pip install ikea_api[driver]
```

# Initialization

```python
from ikea_api import IkeaApi

api = IkeaApi(
    token=...,  # If you already have a token and stored it somewhere
    country_code="ru",
    language_code="ru",
)
```

# Endpoints

## [Authorization](https://github.com/vrslev/ikea-api-client/blob/master/src/ikea_api/auth.py)

### [As Guest](https://github.com/vrslev/ikea-api-client/blob/03c1add4fd03fc41a7fef41c35bd2aa9c0c36d4b/src/ikea_api/auth.py#L35-L35)

```python
api.login_as_guest()
```

First time you open IKEA.com guest token is being generated and stored in Cookies. It expires in 30 days.

### [As Registered User](https://github.com/vrslev/ikea-api-client/blob/03c1add4fd03fc41a7fef41c35bd2aa9c0c36d4b/src/ikea_api/auth.py#L56-L56)

Token lasts 1 day. It may take a while to get authorized token because of Selenium usage.

```python
api.login(username=..., password=...)
```

## [Cart](https://github.com/vrslev/ikea-api-client/blob/master/src/ikea_api/endpoints/cart/__init__.py)

This API endpoint allows you to do everything you would be able to do on the site, and even more:

- Add, Delete and Update items
- Show cart
- Clear cart
- Set and Delete Coupon
- Copy cart from another user

Works with and without authorization. If you logged in all changes apply to the _real_ cart. Use case: programmatically add items to cart and order it manually on IKEA.com.

Example:

```python
cart = api.Cart
cart.add_items({"30457903": 1})
print(cart.show())
```

## [Order Capture](https://github.com/vrslev/ikea-api-client/blob/master/src/ikea_api/endpoints/order_capture/__init__.py)

Check availability for Pickup or Delivery. This is the only way.

If you need to know whether items are available in stores, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

```python
api.OrderCapture(zip_code="101000")
```

## [Purchases](https://github.com/vrslev/ikea-api-client/blob/master/src/ikea_api/endpoints/purchases/__init__.py)

### [Order History](https://github.com/vrslev/ikea-api-client/blob/fc264640ca1f27f4a58c1c57891a917414518a7d/src/ikea_api/endpoints/purchases/__init__.py#L34-L34)

```python
api.login(username=..., password=...)
history = api.Purchases.history()
```

### [Order Info](https://github.com/vrslev/ikea-api-client/blob/fc264640ca1f27f4a58c1c57891a917414518a7d/src/ikea_api/endpoints/purchases/__init__.py#L44-L44)

```python
api.login(username=..., password=...)
order = api.Purchases.order_info(order_number=...)

# Or use it without authorization, email is required
api.login_as_guest()
order = api.order_info(order_number=..., email=...)
```

## [Item Specs](https://github.com/vrslev/ikea-api-client/tree/master/src/ikea_api/endpoints/item)

Get information about item by item number

```python
item_codes = ["30457903"]

items = api.fetch_items_specs.iows(item_codes)

# or
items = api.fetch_items_specs.ingka(item_codes)

# or
item_codes_dict = {d: True for d in items}  # True — is SPR i. e. combination
items = api.fetch_items_specs.pip(item_codes_dict)
```

There are many ways because information about some items is not available in some endpoints.

# Response Examples

You can review response examples for all endpoint before using it [here](https://github.com/vrslev/ikea-api-client/tree/master/response_examples)
