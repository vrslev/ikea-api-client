Client for several IKEA APIs.

[![Version](https://img.shields.io/pypi/v/ikea_api?color=green&label=version)](https://pypi.org/project/ikea_api/)
[![Python Version](https://img.shields.io/pypi/pyversions/ikea_api?color=green)](https://pypi.org/project/ikea_api/)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?color=green)](https://pypi.org/project/ikea_api/)
[![License](https://img.shields.io/pypi/l/ikea_api?color=green)](https://github.com/vrslev/ikea-api-client/blob/main/LICENSE)

# Features

- Log In (as guest or as user),
- Manage Cart,
- Check available Delivery Services,
- Retrieve Purchases History and information about specific order,
- Get Product information.

# Installation

```bash
pip install ikea_api
```

To use authorization as registered user you need to have Chrome on board.

# Usage

```python
from ikea_api import IkeaApi

ikea = IkeaApi(
    token=None,
    country_code="us",
    language_code="en",
)
```

Examples below don't show everything you can do, but this package is almost fully typed and quite small. So, better browse code or use autocompletion in your IDE 😄

## Endpoints

### 🔑 Authorization

#### [As Guest](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/auth.py#L19)

First time you open IKEA.com, guest token is being generated and stored in cookies. It expires in 30 days.

```python
ikea.login_as_guest()
```

#### [As Registered User](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/auth.py#L117)

Token lasts 1 day. It may take a while to get authorized token because of it uses headless Chrome to proceed. Note, that Chrome is required to login.

```python
ikea.login(username=..., password=...)
```

📌 You probably don't want to re-login every time (this is quite suspicious behavior from IKEA's perspective). This package doesn't store tokens, so, make sure to take care of it yourself.

To show token, use this method:

```python
ikea.reveal_token()
```

### [🛒 Cart](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/endpoints/cart/__init__.py#L26)

This API endpoint allows you to do everything you would be able to do on the site, and even more:

- Add, delete and update items,
- Set or delete Coupon,
- Show it,
- Clear it,
- And even copy another user's cart.

Authorization as user is optional. All changes apply to the _real_ cart if you're logged in. **Use case:** programmatically add items to cart and order it manually on IKEA.com.

Simple example:

```python
ikea.Cart.add_items({"30457903": 1})  # { item_code: quantity }
print(ikea.Cart.show())
```

### [🚛 Order Capture](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/endpoints/order_capture/__init__.py#L12)

Check Pickup or Delivery availability.

```python
ikea.OrderCapture(
    zip_code="02215",
    state_code="MA",  # pass state code only if you're in USA
)
```

If you need to know whether items are available in stores, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

### 📦 Purchases

#### [Order History](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/endpoints/purchases/__init__.py#L42)

```python
ikea.Purchases.history()
```

#### [Order Info](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/endpoints/purchases/__init__.py#L52)

```python
ikea.Purchases.order_info(order_number=...)

# Or use it without authorization, email is required
ikea.Purchases.order_info(order_number=..., email=...)
```

### [🪑 Item Information](https://github.com/vrslev/ikea-api-client/tree/main/src/ikea_api/endpoints/item)

Get information about Item by item number.

There are many ways because information about some items is not available in some endpoints.

```python
item_codes = ("30457903",)

items = ikea.fetch_items_specs.iows(item_codes)

# or
items = ikea.fetch_items_specs.ingka(item_codes)

# or
item_codes_dict = {"30457903": False}  # { item_code: is_combination }
items = ikea.fetch_items_specs.pip(item_codes_dict)
```
