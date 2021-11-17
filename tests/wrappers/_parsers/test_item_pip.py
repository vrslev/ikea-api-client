from typing import Any

import pytest
from pydantic import ValidationError

from ikea_api.wrappers._parsers.item_pip import (
    Catalog,
    CatalogRef,
    CatalogRefs,
    get_category_name_and_url,
    main,
)


def generate_catalog_refs(name: str, url: str):
    return CatalogRefs(products=CatalogRef(elements=[Catalog(name=name, url=url)]))


def test_get_category_name_and_url_passes():
    name, url = "Книжные шкафы", "https://www.ikea.com/ru/ru/cat/knizhnye-shkafy-10382/"
    assert get_category_name_and_url(generate_catalog_refs(name, url)) == (name, url)


def test_get_category_name_and_url_raises():
    name, url = "Книжные шкафы", "not a url"
    with pytest.raises(ValidationError):
        generate_catalog_refs(name, url)


test_data = (
    {
        "name": "default",
        "response": {
            "id": "30379118",
            "globalId": "40346924",
            "name": "KALLAX КАЛЛАКС",
            "typeName": "Стеллаж",
            "validDesignText": "серый/под дерево",
            "mainImage": {
                "alt": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                "id": "0494558_PE627165",
                "imageFileName": "0494558_PE627165_S5.JPG",
                "url": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s5.jpg",
                "type": "MAIN_PRODUCT_IMAGE",
            },
            "pipUrl": "https://www.ikea.com/ru/ru/p/kallax-kallaks-stellazh-seryy-pod-derevo-30379118/",
            "price": "7 999 ₽",
            "priceNumeral": 7999,
            "priceExclTax": "6 665.83 ₽",
            "priceExclTaxNumeral": 6665.83,
            "currencyCode": "RUB",
            "revampPrice": {
                "numDecimals": 0,
                "separator": ".",
                "integer": "7 999",
                "decimals": "",
                "currencySymbol": " ₽",
                "currencyPrefix": "",
                "currencySuffix": " ₽",
                "hasTrailingCurrency": True,
            },
            "catalogRefs": {
                "products": {
                    "id": "products",
                    "name": "Товары",
                    "url": "https://www.ikea.com/ru/ru/cat/tovary-products/",
                    "elements": [
                        {
                            "id": "10382",
                            "name": "Книжные шкафы",
                            "url": "https://www.ikea.com/ru/ru/cat/knizhnye-shkafy-10382/",
                        },
                        {
                            "id": "10412",
                            "name": "Серванты и буфеты",
                            "url": "https://www.ikea.com/ru/ru/cat/servanty-i-bufety-10412/",
                        },
                        {
                            "id": "11465",
                            "name": "Стеллажи",
                            "url": "https://www.ikea.com/ru/ru/cat/stellazhi-11465/",
                        },
                        {
                            "id": "55012",
                            "name": "Шкафы ЭКЕТ",
                            "url": "https://www.ikea.com/ru/ru/cat/shkafy-eket-55012/",
                        },
                    ],
                },
                "series": {
                    "id": "series",
                    "name": "Серии",
                    "url": "https://www.ikea.com/ru/ru/cat/serii-series/",
                    "elements": [
                        {
                            "id": "27534",
                            "name": "КАЛЛАКС серия",
                            "url": "https://www.ikea.com/ru/ru/cat/kallaks-seriya-27534/",
                        }
                    ],
                },
            },
            "experimental": {
                "isBreathTakingItem": False,
                "isFamilyPrice": False,
                "isNewLowerPrice": False,
                "isNewProduct": False,
                "isTimeRestricted": False,
                "rating": {
                    "value": 0,
                    "maxValue": 5,
                    "count": 0,
                    "percentage": 0,
                    "enabled": True,
                },
                "technicalCompliance": {"valid": False},
                "priceUnit": "",
                "contextualImage": {
                    "alt": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                    "id": "1051326_PE845149",
                    "imageFileName": "1051326_PE845149_S5.JPG",
                    "url": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s5.jpg",
                    "type": "CONTEXT_PRODUCT_IMAGE",
                },
            },
        },
    },
)


@pytest.mark.parametrize("test_data_response", test_data)
def test_main(test_data_response: dict[str, Any]):
    main(test_data_response["response"])
