Client for several IKEA APIs.

[![Test](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml/badge.svg)](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/ikea_api?label=Python)](https://pypi.org/project/ikea_api)
[![Downloads](https://img.shields.io/pypi/dm/ikea_api?label=Downloads&color=blueviolet)](https://pypi.org/project/ikea_api)

# Features

With this library you can access following IKEA's APIs:

- Cart,
- Home Delivery and Collect Services (actually, Order Capture),
- Items info (3 different services),
- 3D models,
- Purchases (history and order info),
- Search,
- Stock.

Also the package:

- Is **backend agnostic**: choose HTTP library you want (async, too!),
- Is **fully typed and tested**,
- Has optional wrappers around some APIs based on Pydantic.

# Installation

```bash
pip install ikea_api
```

- Use [httpx](https://www.python-httpx.org) — awesome async HTTP library — as backend:

```bash
pip install "ikea_api[httpx]"
```

- Use [requests](https://docs.python-requests.org) as backend:

```bash
pip install "ikea_api[requests]"
```

- Use wrappers:

```bash
pip install "ikea_api[wrappers]"
```

- Install everything:

```bash
pip install "ikea_api[all]"
```

# Usage

_ikea_api_ is unusual API client. It decouples I/O from logic for easier testing and maintenance. As a bonus, you can use literally _any_ HTTP library.
Let's have a look at how to work with ikea_api.

```python
import ikea_api

# Constants like country, language, base url
constants = ikea_api.Constants(country="us", language="en")
# Search API
search = ikea_api.Search(constants)
# Search endpoint with prepared data
endpoint = search.search("Billy")
```

As you can see, nothing happened up to this point. Code suggests that we already should get the result of the search but we don't. What happened is `search()` returned a data class that contains information about endpoint that can be interpreted by an endpoint runner. There are two built-in: for [requests](https://docs.python-requests.org) (sync) and [httpx](https://www.python-httpx.org) (async), but you can easily write one yourself.

Here's how you would use _requests_ one:

```python
ikea_api.run(endpoint)
```

And _httpx_ one:

```python
await ikea_api.run_async(endpoint)
```

`ikea_api.run_async()` is async function, so you have to "await" it or run using `asyncio.run()`.

## Endpoints reference

### 🔑 Authorization

First time you open ikea.com, guest token is being generated and stored in cookies. Same thing must be done in here before using any endpoint.

This token expires in 30 days.

```python
ikea_api.Auth(constants).get_guest_token()
```

Previously you could login as user (with login and password), but now there's very advanced telemetry that I wouldn't be able to solve in hundred years 🤪

### 🛒 Cart

With this endpoint you can do everything you can using IKEA's frontend:

```python
cart = ikea_api.Cart(constants, token=...)
```

- Show the cart

```python
cart.show()
```

- Clear it

```python
cart.clear()
```

- Add, update and delete items

```python
cart.add_items({"30457903": 1})  # { item_code: quantity }

cart.update_items({"30457903": 5})

cart.remove_items(["30457903"])
```

- Set and clear coupon

```python
cart.set_coupon(...)

cart.clear_coupon()
```

- and even copy another user's cart.

```python
cart.copy_items(source_user_id=...)
```

You can edit your user's actual cart if you use authorized token (copy-paste from cookies).

> 💡 There's wrapper that clears current cart and adds items with error handling: if requested item doesn't exist, the function just skips it and tries again.
>
> ```python
> ikea_api.add_items_to_cart(  # Function returns items that can't be added. In this case: ['11111111']
>     cart=cart,
>     items={
>         "30457903": 1,
>         "11111111": 2,  # invalid item that will be skipped
>     },
> )
> ```

### 🚛 Order Capture

Check pickup or delivery availability. If you need to know whether items are available _in stores_, use [Item availability endpoint](#%F0%9F%9F%A2-item-availability) or [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).

```python
order = ikea_api.OrderCapture(constants, token=token)

cart_show = run(cart.show())
items = ikea_api.convert_cart_to_checkout_items(cart_show)

checkout_id = run(order.get_checkout(items))
service_area_id = run(
    order.get_service_area(
        checkout_id,
        zip_code="02215",
        state_code="MA",  # pass State Code only if your country has them
    )
)
home_services = run(order.get_home_delivery_services(checkout_id, service_area_id))
collect_services = run(
    order.get_collect_delivery_services(checkout_id, service_area_id)
)
```

> 💡 You can use wrapper to add items to cart (clearing cart before and handling unknown item errors if they appear) and parse response in nice Pydantic models:
>
> ```python
> services = await ikea_api.get_delivery_services(
>     constants=constants,
>     token=...,
>     items={
>         "30457903": 1,
>         "11111111": 2,  # invalid item that will be skipped
>     },
>     zip_code="101000",
> )
> services.delivery_options  # List of parsed delivery services
> services.cannot_add  # ['11111111']
> ```

### 📦 Purchases

```python
purchases = ikea_api.Purchases(constants, token=token)
```

#### History

This method requires authentication, so if you don't have authorized token, it won't work.

```python
purchases.history()

# Get all purchases:
purchases.history(take=10000)

# Pagination:
purchases.history(take=10, skip=1)
```

> 💡 Get parsed response with the wrapper:
>
> ```python
> ikea_api.get_purchase_history(purchases)  # Returns a list of parsed purchases
> ```

#### Order info

```python
purchases.order_info(order_number=..., email=...)

# If you have authorized token, you can drop email:
purchases.order_info(order_number="111111111")

# The method also has other params but they're mostly internal:
purchases.order_info(
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
> ikea_api.get_purchase_info(  # Returns parsed purchase object. Items are not listed.
>    purchases=purchases,
>    order_number=...,
>    email=...,
> )
> ```

### 🪑 Item info

Get item specification by item code (product number or whatever). There are 3 endpoints to do this because you can't get all the data about all the items using only one endpoint.

```python
iows_items = ikea_api.IowsItems(constants)
iows_items.get_items(["30457903"])

ingka_items = ikea_api.IngkaItems(constants)
ingka_items.get_items(["30457903"])

pip_item = ikea_api.PipItem(constants)
pip_item.get_item("30457903")
```

> 💡 You probably won't want to use raw APIs when there's convenient "smart" wrapper that combines them all and parses basic info:
>
> ```python
> ikea_api.get_items(["30457903"])
> ```

### 📦 Item 3D models

Get 3D models by item code.

```python
rotera_item = ikea_api.RoteraItem(constants)
rotera_item.get_item("30221043")
```

### 🟢 Item availability

Get availability by item code (product number or whatever).

```python
stock = ikea_api.Stock(constants)
stock.get_stock("30457903")
```

### 🔎 Search

Search for products in the product catalog by product name. Optionally also specify a maximum amount of returned search results (defaults to 24) and types of required search results.

```python
search = ikea_api.Search(constants)
search.search("Billy")

# Retrieve 10 search results (default is 24)
search.search("Billy", limit=10)

# Configure search results types
search.search(
    "Billy",
    types=...,  # Combine any of: ["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]
)
```

### 🛠 Utilities

#### Parse item codes

Parse item codes from string or list.

```python
assert ikea_api.parse_item_codes("111.111.11") == ["11111111"]
assert ikea_api.parse_item_codes("11111111, 222.222.22") == ["11111111", "22222222"]
assert ikea_api.parse_item_codes("111") == []
```

#### Format item code

Parse item code and format it.

```python
assert ikea_api.format_item_code("11111111") == "111.111.11"
assert ikea_api.format_item_code("111-111-11") == "111.111.11"
assert ikea_api.format_item_code("111.111.11") == "111.111.11"
```
