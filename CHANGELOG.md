<!-- prettier-ignore-start -->
# Changelog

<!--next-version-placeholder-->

## v1.1.6 (2022-02-02)
### Fix
* **Order Capture parser:** Allow optional possibleDeliveries ([`9dce4e7`](https://github.com/vrslev/ikea-api-client/commit/9dce4e7089a1fc22c74367874fbb206d65a01e74))

### Chore
* Enable `reportUnnecessaryTypeIgnoreComment` ([`b2243dc`](https://github.com/vrslev/ikea-api-client/commit/b2243dc4f6d2c3fb53a926e25999111ad70e932c))
* **deps-dev:** Update black requirement from 21.12b0 to 22.1.0 ([#88](https://github.com/vrslev/ikea-api-client/issues/88)) ([`3168ec5`](https://github.com/vrslev/ikea-api-client/commit/3168ec5fcfbbd2ebdc00723e7a1dff0078e9d49e))
* **deps:** Update pre-commit hooks ([#89](https://github.com/vrslev/ikea-api-client/issues/89)) ([`06756e5`](https://github.com/vrslev/ikea-api-client/commit/06756e514cb6655af252bcd88c141ddc60aa91ba))
* **deps-dev:** Update pre-commit requirement from 2.16.0 to 2.17.0 ([#86](https://github.com/vrslev/ikea-api-client/issues/86)) ([`7324d39`](https://github.com/vrslev/ikea-api-client/commit/7324d39ae3b481eb2006281c31bc17c2ec524f17))

## v1.1.5 (2022-01-23)
### Fix
* **Item wrapper:** Make ingka-pip endpoints default option since IOWS API is deprecated ([`c549022`](https://github.com/vrslev/ikea-api-client/commit/c5490224b2bffc7d183fb13a7095fc2735e21958))
* **Item Ingka parser:** Allow optional media field ([`53df94e`](https://github.com/vrslev/ikea-api-client/commit/53df94e9a78ab2db710c34265187477e22df4a8f))
* **Items parsers:** Return parsed item code from ItemCode type validation ([`5f7881e`](https://github.com/vrslev/ikea-api-client/commit/5f7881e00fb2880874a4d2ec217244f68c33ba79))

### Chore
* Add Python 3.10 to target versions for Black ([`189179b`](https://github.com/vrslev/ikea-api-client/commit/189179b0d78eadcda9868db22930abd4d5731d0a))
* **deps:** Update responses requirement from 0.16.0 to 0.17.0 ([#84](https://github.com/vrslev/ikea-api-client/issues/84)) ([`62e0339`](https://github.com/vrslev/ikea-api-client/commit/62e0339aa5be729837c4dfb238bf61771142f767))
* **deps:** Update pytest-randomly requirement from 3.10.3 to 3.11.0 ([#85](https://github.com/vrslev/ikea-api-client/issues/85)) ([`b8a7af6`](https://github.com/vrslev/ikea-api-client/commit/b8a7af6513ea4a204d5ed229b69f43e6121d7f64))

## v1.1.4 (2022-01-08)
### Fix
* **Order Capture parser:** Don't return unavailable options that don't have unavailable items ([`f523aaa`](https://github.com/vrslev/ikea-api-client/commit/f523aaa48b40c09cec4bf79160b2f115a1eea36a))
* **Order Capture:** Remove unused error handling ([`5c0d495`](https://github.com/vrslev/ikea-api-client/commit/5c0d4954a55b2172aa44b4b23591ccedad831969))

## v1.1.3 (2022-01-05)
### Fix
* **utils:** Allow passing empty list to `parse_item_codes` ([`c91beb3`](https://github.com/vrslev/ikea-api-client/commit/c91beb33012c8d6db8e778b9d475a94583022237))

## v1.1.2 (2022-01-04)
### Fix
* **Item Iows parser:** Allow optional RetailItemCommPackageMeasureList ([`d09d057`](https://github.com/vrslev/ikea-api-client/commit/d09d0577b7d2d89efc25c63bbecdf2fbca702ad5))

### Chore
* Fix typing issues ([`a7ab225`](https://github.com/vrslev/ikea-api-client/commit/a7ab225d43ff4ab079fbc91fa36a115bddacd658))
* **deps:** Update pre-commit hooks ([#81](https://github.com/vrslev/ikea-api-client/issues/81)) ([`1006ede`](https://github.com/vrslev/ikea-api-client/commit/1006edeea006951513c1272a1014f562351b74c9))

## v1.1.1 (2021-12-29)
### Fix
* **Order Capture parser:** Failing case where service.possibleDeliveries is None ([`bacb98c`](https://github.com/vrslev/ikea-api-client/commit/bacb98c63be05972f40b8c7791d24a6f0c2dbde7))

## v1.1.0 (2021-12-28)
### Feature
* Update Order Capture API ([#80](https://github.com/vrslev/ikea-api-client/issues/80)) ([`c4391a4`](https://github.com/vrslev/ikea-api-client/commit/c4391a411ae598ec6f1b5dfa716a7fcfd3508579))

### Chore
* **deps:** Update pre-commit hooks ([`a6a8893`](https://github.com/vrslev/ikea-api-client/commit/a6a8893178460ab201165e1241a067bd16f90594))
* Fix typo in CHANGELOG.md ([`4f5f573`](https://github.com/vrslev/ikea-api-client/commit/4f5f57350f4c7dba4e85144d6ba78285973d0be5))
* **deps-dev:** Update pre-commit requirement from 2.15.0 to 2.16.0 ([`1dcb87b`](https://github.com/vrslev/ikea-api-client/commit/1dcb87b6deca7c826314b320c3f6fba20eaed1aa))
* **deps:** Update pytest-randomly requirement from 3.10.2 to 3.10.3 ([`b2b8d1f`](https://github.com/vrslev/ikea-api-client/commit/b2b8d1ff7341e9972fd176c5dd90e1875c8aaf44))
* **deps-dev:** Update black requirement from 21.11b1 to 21.12b0 ([`78214b5`](https://github.com/vrslev/ikea-api-client/commit/78214b50b53301a8fc07f1b4ac334933af676140))
* **deps:** Update pre-commit hooks ([`422e84d`](https://github.com/vrslev/ikea-api-client/commit/422e84db63785d6ff71631c5015e703bbf0d0fc6))

## v1.0.3 (2021-12-05)
### Fix
* **`add_items_to_cart`:** Allow missing key in error dict ([`e20033a`](https://github.com/vrslev/ikea-api-client/commit/e20033a6b18c72b61bbdf3bad5e40a343311e502))
* **OrderCapture fetcher:** Don't throw on no pickup points available error ([`14017f6`](https://github.com/vrslev/ikea-api-client/commit/14017f60e989f1970aeb8ee67d00950b43bfe7f8))
* **typing:** Add missing type hint ([`eba9a1c`](https://github.com/vrslev/ikea-api-client/commit/eba9a1c8ab3695c35539a45cf03529af3bd7a3cd))
* **Item Iows fetcher:** Kindly return empty list if received no data at all ([`a0ca38a`](https://github.com/vrslev/ikea-api-client/commit/a0ca38a31a3c530055d91fd1a29fe75b9d86f765))

### Chore
* **deps:** Update pre-commit hooks ([`cdd9fe5`](https://github.com/vrslev/ikea-api-client/commit/cdd9fe58c7a50fa3adfa479a52573d44422ee6bb))
* **deps:** Update responses requirement from 0.15.0 to 0.16.0 ([`751ce82`](https://github.com/vrslev/ikea-api-client/commit/751ce82685e7694cccfd9cc41a9730d77b8cceff))
* **deps-dev:** Update black requirement from 21.10b0 to 21.11b1 ([`55a00a3`](https://github.com/vrslev/ikea-api-client/commit/55a00a34414942ec31613ac508473868bc2b75bd))

## v1.0.2 (2021-11-26)
### Fix
* **wrappers:** Allow dict (means error) in `ImageUrl` and not list in `RetailItemCommChild` in Item Iows parser ([#71](https://github.com/vrslev/ikea-api-client/issues/71)) ([`bcf7ad7`](https://github.com/vrslev/ikea-api-client/commit/bcf7ad740ec6073038ac6a80f379273991f3e538))

## v1.0.1 (2021-11-25)
### Fix
* **wrappers:** Allow empty response in Item Pip parser ([`115f574`](https://github.com/vrslev/ikea-api-client/commit/115f574de67fa0c59e3da1e1ff7c76653cbf0b4e))
* **wrappers:** Allow optional `catalogRefs` in Item Pip parser ([`e3fee53`](https://github.com/vrslev/ikea-api-client/commit/e3fee5318333d3ef6a8dcf0cc3c46e8cc970f08d))
* **wrappers:** Parse item codes (allow raw ones) in item parsers ([`55c01d5`](https://github.com/vrslev/ikea-api-client/commit/55c01d5a0b4a79a153b232b178f04bb435ce6bba))
* **wrappers:** Allow `CatalogRef` to be not list in Item Iows parser ([`a935f4a`](https://github.com/vrslev/ikea-api-client/commit/a935f4ab89595cd5fb0175ec199750849e474850))
* **wrappers:** Allow optional `CatalogRef` in Item Iows parser ([`525f3e9`](https://github.com/vrslev/ikea-api-client/commit/525f3e9fa04e101a6f0ba53065393fa76da6701c))
* **wrappers:** Allow optional `ValidDesignText` in Item Iows parser ([`c82885b`](https://github.com/vrslev/ikea-api-client/commit/c82885bf107ca392f65c40632ab56166173a9fea))
* Add missing type hints ([`aa1e25b`](https://github.com/vrslev/ikea-api-client/commit/aa1e25bf4e9d99fe0f5e8d9d5709208f4d53e12a))

## v1.0.0 (2021-11-25)
### Feature
* Prepare for major release ([#69](https://github.com/vrslev/ikea-api-client/issues/69)) ([`8e72a16`](https://github.com/vrslev/ikea-api-client/commit/8e72a165bbebc1e2aa96ea772d0fe94df85ad0c1))
* Merge ikea-api-wrapped ([#64](https://github.com/vrslev/ikea-api-client/issues/64)) ([`4a199e3`](https://github.com/vrslev/ikea-api-client/commit/4a199e3d71dcda492241fc343b291226885e201b))

### Chore
* Add codecov integration ([#68](https://github.com/vrslev/ikea-api-client/issues/68)) ([`7cc0c83`](https://github.com/vrslev/ikea-api-client/commit/7cc0c8332f2c8697f575b27b0d8076930fce0db0))
* **deps:** Update pre-commit hooks ([`ca89130`](https://github.com/vrslev/ikea-api-client/commit/ca891308b3e990411a7ce337df88300d4e5a60bd))
* **pre-commit:** Remove setup-cfg-fmt hook ([`5cbe1e9`](https://github.com/vrslev/ikea-api-client/commit/5cbe1e949ef1a91a4e7c8d6bbd7c4c4864563e20))

## v0.10.0 (2021-11-16)
### Feature
* Move to Poetry, improve CI ([#59](https://github.com/vrslev/ikea-api-client/issues/59)) ([`9f136a7`](https://github.com/vrslev/ikea-api-client/commit/9f136a79a9b78aa5bf438d32b04b7bbcff0ec7f5))
* Refactoring, tests ([#42](https://github.com/vrslev/ikea-api-client/issues/42)) ([`63b029c`](https://github.com/vrslev/ikea-api-client/commit/63b029c20fbfd593ee44b1b6132ca26a69264729))

### Build
* Remove aiohttp dependency ([`17bec36`](https://github.com/vrslev/ikea-api-client/commit/17bec369741e26c75245ce9273590cd4b4117528))

### Chore
* **README:** Change link in Version badge ([`c29a515`](https://github.com/vrslev/ikea-api-client/commit/c29a51531e2c0cdc2788a081329f0f1f7aa5feae))
* **README:** Add Test badge, change colors and names ([`69a5277`](https://github.com/vrslev/ikea-api-client/commit/69a52777320ce1b8e00f7df4a8c47fe62b5823f5))
* **README:** Fix GitHub permalinks ([`3711377`](https://github.com/vrslev/ikea-api-client/commit/3711377b55c86f4b40415716e9708703931df060))
* Remove "Log In" feature from README ([`61147b4`](https://github.com/vrslev/ikea-api-client/commit/61147b4af229af189881a869b2ce12f6a7750bc6))
* **deps:** Update responses requirement from ^0.15.0 to ^0.16.0 ([`6b3a543`](https://github.com/vrslev/ikea-api-client/commit/6b3a543442c48d80891253cb34e756bd82b6b870))
* **deps-dev:** Bump black from 21.9b0 to 21.10b0 ([`af5b114`](https://github.com/vrslev/ikea-api-client/commit/af5b114aa83e1b7766b00f8bdb536d38e1c1adaf))
* **deps:** Bump typing-extensions from 3.10.0.2 to 4.0.0 ([#58](https://github.com/vrslev/ikea-api-client/issues/58)) ([`e39d51c`](https://github.com/vrslev/ikea-api-client/commit/e39d51ccbd3b2f74096495e1abdd422dbf311cfe))
* **deps:** Update pre-commit hooks ([`defd52e`](https://github.com/vrslev/ikea-api-client/commit/defd52ed0f6c427ab8774f563bb34dbc62ec9792))

## v0.9.0 (2021-11-06)
### Feature
* Remove code relevant to authorized token ([`8ed46be`](https://github.com/vrslev/ikea-api-client/commit/8ed46bec9d0d27d695dd9c66f68f25e02299f60c))

## v0.8.1 (2021-11-06)
### Fix
* **auth:** Save screenshot ([`05e0651`](https://github.com/vrslev/ikea-api-client/commit/05e06514c77b41c5e98614c6877a53f1ea336bb5))

## v0.8.0 (2021-09-27)
### Feature
* Add search functionality ([#44](https://github.com/vrslev/ikea-api-client/issues/44)) ([`c30e3a7`](https://github.com/vrslev/ikea-api-client/commit/c30e3a794c796aa7a092c0c8ac47c19615f2836f))

## v0.7.2 (2021-09-09)
### Fix
* Stop trying to show pretty error message ([`e6e5f57`](https://github.com/vrslev/ikea-api-client/commit/e6e5f57a6ff5648dbda48c9150e9f73d6573a61b))

## v0.7.1 (2021-09-09)
### Fix
* OrderCapture for Sweden (merge PR #40) ([`4821a5e`](https://github.com/vrslev/ikea-api-client/commit/4821a5eb86dd431f75b89d43ca6e9a7e4587997e))

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
