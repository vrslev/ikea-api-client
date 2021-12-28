Client for several IKEA APIs.

[![Test](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml/badge.svg)](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/vrslev/ikea-api-client/branch/main/graph/badge.svg?token=Z1G75NBIC0)](https://codecov.io/gh/vrslev/ikea-api-client)
[![Version](https://img.shields.io/github/v/release/vrslev/ikea-api-client?label=Version)](https://github.com/vrslev/ikea-api-client/releases/latest)
[![Python](https://img.shields.io/pypi/pyversions/ikea_api?label=Python)](https://pypi.org/project/ikea_api)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?label=Downloads)](https://pypi.org/project/ikea_api)
[![License](https://img.shields.io/pypi/l/ikea_api?label=License)](https://github.com/vrslev/ikea-api-client/blob/main/LICENSE)

# Features

With this library you can access the following IKEA's APIs:

- Cart,
- Delivery Services (actually, Order Capture),
- Purchases (history and order info),
- Items info (3 different services),
- Search.

Also:

- Fully typed and tested,
- Has wrappers around most of APIs based on Pydantic.

# Installation

```bash
pip install ikea_api
```

If you intend to use wrappers:

```bash
pip install "ikea_api[wrappers]"
```

# Usage

`IKEA` object unites all available the APIs that are in this package. This is done to share token, country and language.

```python
from ikea_api import IKEA

ikea = IKEA(token=None, country_code="ru", language_code="ru")
```

## Endpoints reference

### 🔑 [Authorization](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/auth.py)

First time you open IKEA.com, guest token is being generated and stored in cookies. Same thing must be done in here before using any endpoint.

This token expires in 30 days.

```python
ikea.login_as_guest()
```

It is stored in `token` property:

```python
ikea.token  # Outputs JWT token
```

Previously you could login as user (with login and password), but now there's very advanced telemetry that I wouldn't be able to solve in hundred years 🤪

### 🛒 [Cart](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/cart.py)

With this endpoint you can do everything you can using IKEA's frontend:

- Show the cart

```python
ikea.cart.show()
```

- Clear it

```python
ikea.cart.clear()
```

- Add, update and delete items

```python
ikea.cart.add_items({"30457903": 1})  # { item_code: quantity }

ikea.cart.update_items({"30457903": 5})

ikea.cart.remove_items(["30457903"])
```

- Set and clear coupon

```python
ikea.cart.set_coupon(...)

ikea.cart.clear_coupon()
```

- and even copy another user's cart.

```python
ikea.cart.copy_items(source_user_id=...)
```

If you use authorized token (copy-paste from cookies), than you edit your user's actual cart.

> 💡 There's wrapper that clears current cart and adds items with error handling: if requested item doesn't exist, the function just skips it and tries again.
>
> ```python
> from ikea_api.wrappers import add_items_to_cart
>
> add_items_to_cart(  # Function returns items that can't be added. In this case: ['11111111']
>     ikea,
>     items={
>         "30457903": 1,
>         "11111111": 2,  # invalid item that will be skipped
>     },
> )
> ```

### 🚛 [Order Capture](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/order_capture.py)

Check pickup or delivery availability. If you need to know whether items are available _in stores_, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

```python
order = ikea.order_capture(
    zip_code="02215",
    state_code="MA",  # pass State Code only if your country has them
)
home_delivery_services = order.get_home_delivery_services()
collect_delivery_services = order.get_collect_delivery_services()
```

> 💡 You can use wrapper to add items to cart (clearing cart before and handling unknown item errors if they appear) and parse response in nice Pydantic models:
>
> ```python
> from ikea_api.wrappers import get_delivery_services
>
> res = get_delivery_services(
>    ikea,
>    items={
>        "30457903": 1,
>        "11111111": 2,  # invalid item that will be skipped
>    },
>    zip_code="101000",
> )
> res.delivery_options  # List of parsed delivery services
> res.cannot_add  # ['11111111']
> ```

### 📦 [Purchases](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/purchases.py)

#### History

This method requires authentication, so if you don't have authorized token, it won't work.

```python
ikea.purchases.history()

# Get all purchases:
ikea.purchases.history(take=10000)

# Pagination:
ikea.purchases.history(take=10, skip=1)
```

> 💡 Get parsed response with the wrapper:
>
> ```python
> from ikea_api.wrappers import get_purchase_history
>
> get_purchase_history(ikea)  # Returns list of parsed purchases
> ```

#### Order info

```python
ikea.purchases.order_info(order_number=..., email=...)

# If you have authorized token, you can drop email:
ikea.purchases.order_info(order_number="111111111")

# The method also has other params but they're mostly internal:
ikea.purchases.order_info(
    order_number=...,
    email=...,
    queries=...,  # Queries that will be included in request, combine any of: ["StatusBannerOrder", "CostsOrder", "ProductListOrder"]. By default, all of them are included.
    # Params below are relevant to ProductListOrder
    skip_products=...,
    skip_product_prices=...,
    take_products=...,
)
```

> 💡 Get parsed response with the wrapper:
>
> ```python
> from ikea_api.wrappers import get_purchase_info
>
> get_purchase_info(  # Returns parsed purchase object. Items are not listed.
>    ikea,
>    id=...,
>    email=...,
> )
> ```

### 🪑 Item info

Get item specification by item code (product number or whatever). There are 3 endpoints to do this because you can't get all the data about all the items using only one endpoint.

```python
from ikea_api import IowsItems, IngkaItems, PipItem

item_code = "30457903"
item_codes = [item_code]

# <=90 items at a time
IowsItems()([item_codes])

# <=50 items at a time
IngkaItems()([item_codes])

# 1 item at a time
PipItem()(item_code)
```

> 💡 You probably won't want to use raw APIs when there's convenient "smart" wrapper that combines them all and parses basic info:
>
> ```python
> from ikea_api.wrappers import get_items
>
> get_items(["30457903"])
> ```

### 🔎 [Search](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/search.py)

Search for products in the product catalog by product name. Optionally also specify a maximum amount of returned search results (defaults to 24) and types of required search results.

```python
ikea.search("Billy")

# Retrieve 10 search results (default is 24)
ikea.search("Billy", limit=10)

# Configure search results types
ikea.search(
    "Billy",
    types=...,  # Combine any of: ["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]
)
```

### Utilities

#### Parse item codes

Parse item codes from string or list.

```python
from ikea_api import parse_item_codes

assert parse_item_codes("111.111.11") == ["11111111"]
assert parse_item_codes("11111111, 222.222.22") == ["11111111", "22222222"]
assert parse_item_codes("111") == []
```

#### Format item code

Parse item code and format it.

```python
from ikea_api import format_item_code

assert format_item_code("11111111") == "111.111.11"
assert format_item_code("111-111-11") == "111.111.11"
assert format_item_code("111.111.11") == "111.111.11"
```
