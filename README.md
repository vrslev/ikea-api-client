Client for several IKEA APIs.

[![Test](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml/badge.svg)](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/vrslev/ikea-api-client/branch/main/graph/badge.svg?token=Z1G75NBIC0)](https://codecov.io/gh/vrslev/ikea-api-client)
[![Version](https://img.shields.io/github/v/release/vrslev/ikea-api-client?label=Version)](https://github.com/vrslev/ikea-api-client/releases/latest)
[![Python](https://img.shields.io/pypi/pyversions/ikea_api?label=Python)](https://pypi.org/project/ikea_api)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?label=Downloads)](https://pypi.org/project/ikea_api)
[![License](https://img.shields.io/pypi/l/ikea_api?label=License)](https://github.com/vrslev/ikea-api-client/blob/main/LICENSE)

# Features

- Manage Cart,
- Check available Delivery Services,
- Retrieve Purchases History and information about specific order,
- Get Product information.

# Installation

```bash
pip install ikea_api
```

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

#### [As Guest](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/auth.py)

First time you open IKEA.com, guest token is being generated and stored in cookies. It expires in 30 days.

```python
ikea.login_as_guest()
```

#### As Registered User

You can't do this automatically with this package. IKEA made it nearly impossible to get authorized token. Copy-paste token from ikea.com cookies.

### [🛒 Cart](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/cart.py)

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

### [🚛 Order Capture](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/order_capture.py)

Check Pickup or Delivery availability.

```python
ikea.OrderCapture(
    zip_code="02215",
    state_code="MA",  # pass state code only if you're in USA
)
```

If you need to know whether items are available in stores, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

### 📦 Purchases

#### [Order History](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/purchases.py#L32)

```python
ikea.Purchases.history()
```

#### [Order Info](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/purchases.py#L39)

```python
ikea.Purchases.order_info(order_number=...)

# Or use it without authorization, email is required
ikea.Purchases.order_info(order_number=..., email=...)
```

### 🪑 Item Information

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

### [🔎 Search](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/search.py)

Search for products in the IKEA product catalog by product name. Optionally also specify a maximum amount of returned search results (defaults to 24).

```python
search_results = ikea.Search("Billy")  # Retrieves (at most) 24 search results

# or
search_results = ikea.Search("Billy", 10)  # Retrieves (at most) 10 search results
```
