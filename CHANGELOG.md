<!-- prettier-ignore-start -->
# Changelog

<!--next-version-placeholder-->

## v0.7.0 (2021-09-06)
### Feature
* Add `state_code` field to OrderCapture (merge PR #34) (closes #33) ([`1b9de6e`](https://github.com/vrslev/ikea-api-client/commit/1b9de6e95caa7f4da2c2d25adec5f5817f37a1ef))

## v0.6.3 (2021-09-05)
### Fix
* **Auth:** Guest token payload ([`f316dfd`](https://github.com/vrslev/ikea-api-client/commit/f316dfd1425ba4bc59cd62f655231706b6cc778b))

## v0.6.2 (2021-08-31)
### Fix
* Create new asyncio event loop when using pyppeteer ([`13e67e9`](https://github.com/vrslev/ikea-api-client/commit/13e67e9b05d88b91a3230ddfd319ac5115ca3058))

## v0.6.1 (2021-08-31)
### Fix
* Don't handle SIGINT, SIGTERM, SIGHUP when running pypupeteer in some cases ([`7eb142d`](https://github.com/vrslev/ikea-api-client/commit/7eb142d109f1cbb5913a24dd2d5fb07184f64347))

## v0.6.0 (2021-08-24)
### Feature
* **Auth:** Use pyppeteer for authorization ([`9c25d97`](https://github.com/vrslev/ikea-api-client/commit/9c25d9796b2ec5be7d4db28f07cea5460fa0518f))

### Fix
* **Item:** Use `staticmethod` for various item fetch types ([`2555866`](https://github.com/vrslev/ikea-api-client/commit/2555866921d707ae0d2cac747c83131094104eb6))
* **Item:** If `item_code` param is list, get unique item codes in `parse_item_code` ([`6cbbd06`](https://github.com/vrslev/ikea-api-client/commit/6cbbd06a01e1914cf225a284b6f5f8d932f04e18))

## v0.5.1 (2021-08-08)
### Fix
* GraphqlError—add "errors" attr, error message not causing TypeError ([`6258b70`](https://github.com/vrslev/ikea-api-client/commit/6258b7078aa06df379a26c334793d31666a5d412))

## v0.5.0 (2021-08-06)
### Feature
* Use Poetry as package manager ([`02d45f4`](https://github.com/vrslev/ikea-api-client/commit/02d45f47caad1050c13b513e2966c04d03cf29c8))

## v0.4.1 (2021-08-03)
### Fix
* **OrderCapture:** Add error code to exception ([`455c055`](https://github.com/vrslev/ikea-api-client/commit/455c055694c87403ee2da185d4f8430013386373))

## v0.4.0 (2021-08-03)
### Feature
* **Purchases:** Add ProductListOrder query, allow choosing queries in request, add helpful comments in `fragments` ([`90a94c6`](https://github.com/vrslev/ikea-api-client/commit/90a94c6ad90bd634df3e3277048770209157892e))

### Fix
* Show status code on JSONDecodeError ([`f70a664`](https://github.com/vrslev/ikea-api-client/commit/f70a664a50b3f2e3111fc14c2c3ef2636d8d14f1))

## v0.3.0 (2021-08-03)
### Feature
* **README:** Improve features list ([`70ac22a`](https://github.com/vrslev/ikea-api-client/commit/70ac22af6bdcdc5ce38f6c58e910c6ca188a78ed))
* Add core `IkeaApi` object for ease of usage ([`df8e94a`](https://github.com/vrslev/ikea-api-client/commit/df8e94a6faf33d9f88fea44f5bdf0b7c22d4a4a8))
* Raise if can't find cookie with token in Auth and save screenshot ([`03c1add`](https://github.com/vrslev/ikea-api-client/commit/03c1add4fd03fc41a7fef41c35bd2aa9c0c36d4b))
* Make getting guest token inherit from API class ([`29b6108`](https://github.com/vrslev/ikea-api-client/commit/29b6108b8a72c29a37b32d3018464e73a4ad732e))
* Add method choice in API.call_api ([`49c95ed`](https://github.com/vrslev/ikea-api-client/commit/49c95ed05a554389d51dcc85f32344932425ec27))
* Add `Secrets` class in which is concentrated all the "secret" data ([`4dac46d`](https://github.com/vrslev/ikea-api-client/commit/4dac46d40f40b10dada515dc1138d2d18995a4e9))
* Make `OrderCapture` class callable ([`9c8a619`](https://github.com/vrslev/ikea-api-client/commit/9c8a6191f6a460c7413b2054483beebc6b7599b5))
* Make many variables private ([`0567497`](https://github.com/vrslev/ikea-api-client/commit/05674971c82769098c6e8518b0cc64a970565f63))
* Cover code base with type hints, ([`e8d58e8`](https://github.com/vrslev/ikea-api-client/commit/e8d58e869fda8ad39cb9a0d6a4985e8c12080002))
* Update README: ([`c5e783e`](https://github.com/vrslev/ikea-api-client/commit/c5e783ee400892e9af6d95c9784a80607d63490d))

### Fix
* Semantic release build command ([`e0ef1d6`](https://github.com/vrslev/ikea-api-client/commit/e0ef1d69fb0a1352e92111cffe380410963cc26e))
* Python version in pre-commit action ([`bd23667`](https://github.com/vrslev/ikea-api-client/commit/bd23667455c58775dcb571ac1b9109bdf21384d0))
* **README:** Links to code, grammar, remove link in header `Response Examples` ([`332f455`](https://github.com/vrslev/ikea-api-client/commit/332f45582555194d1c403a15b5f57c17e3d46e3b))
* OrderCapture method ([`6284553`](https://github.com/vrslev/ikea-api-client/commit/62845534805d185aa9fef8c9ffc65e8af214afa8))
* Issues due to latest commit ([`5d6c06a`](https://github.com/vrslev/ikea-api-client/commit/5d6c06a8953c1b4528d339f7d5c8aca91b73b6aa))
* Python 3.7 support ([`924ab0e`](https://github.com/vrslev/ikea-api-client/commit/924ab0e040558d5134526e58fde0a16baea98c86))
* Install pre-commit hooks ([`fda6bdd`](https://github.com/vrslev/ikea-api-client/commit/fda6bdd5da61da45a002871008b373f810aab908))
* **Item:** Annotations, linting issues with `fetch_items_specs` ([`d80bb39`](https://github.com/vrslev/ikea-api-client/commit/d80bb3926248ed2234c4fffb42d61db473d11c5c))
* Python 3.7 support ([`d11258c`](https://github.com/vrslev/ikea-api-client/commit/d11258c1e068c2459e753221bc7e2eb101becdb5))
* Basic error handler ([`bef8498`](https://github.com/vrslev/ikea-api-client/commit/bef8498db5da2d66c89ac3b90f3387a10463efe3))

<!-- prettier-ignore-end -->
