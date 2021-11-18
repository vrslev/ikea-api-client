from types import SimpleNamespace
from typing import Any, Callable

import pytest

from ikea_api._constants import Constants
from ikea_api.wrappers._parsers.item_iows import (
    get_category_name_and_url,
    get_child_items,
    get_image_url,
    get_price,
    get_rid_of_dollars,
    get_url,
    get_weight,
    main,
    parse_weight,
)
from ikea_api.wrappers.types import ChildItemDict


def test_get_rid_of_dollars():
    assert get_rid_of_dollars({"name": {"$": "The Name"}}) == {"name": "The Name"}


def test_get_image_url_filtered():
    assert (
        get_image_url(
            [  # type: ignore
                SimpleNamespace(ImageType="LINE DRAWING"),
                SimpleNamespace(
                    ImageType="not LINE DRAWING", ImageUrl="somename.notpngorjpg"
                ),
            ]
        )
        is None
    )


def test_get_image_url_no_images():
    assert get_image_url([]) is None


@pytest.mark.parametrize("ext", (".png", ".jpg", ".PNG", ".JPG"))
def test_get_image_url_matches(ext: str):
    image: Callable[[str], SimpleNamespace] = lambda ext: SimpleNamespace(
        ImageType="not line drawing", ImageSize="S5", ImageUrl="somename" + ext
    )
    assert (
        get_image_url([image(ext), image(".notpngjpg")])  # type: ignore
        == f"{Constants.BASE_URL}somename{ext}"
    )


def test_get_image_url_first():
    url = "somename.jpg"
    images = [
        SimpleNamespace(ImageType="not line drawing", ImageSize="S4", ImageUrl=url)
    ]
    assert get_image_url(images) == Constants.BASE_URL + url  # type: ignore


@pytest.mark.parametrize(
    ("input", "output"),
    (
        ("10.3 кг", 10.3),
        ("10.45 кг", 10.45),
        ("10 кг", 10.0),
        ("9.415 кг", 9.415),
        ("some string", 0.0),
    ),
)
def test_parse_weight(input: str, output: float):
    assert parse_weight(input) == output


def test_get_weight_no_measurements():
    assert get_weight([]) == 0.0


def test_get_weight_no_weight():
    measurements = [
        SimpleNamespace(
            PackageMeasureType="not WEIGHT", PackageMeasureTextMetric="10.45 м"
        )
    ]
    assert get_weight(measurements) == 0.0  # type: ignore


def test_get_weight_with_input():
    measurements = [
        SimpleNamespace(
            PackageMeasureType="not WEIGHT", PackageMeasureTextMetric="10.45 м"
        ),
        SimpleNamespace(
            PackageMeasureType="WEIGHT", PackageMeasureTextMetric="9.67 кг"
        ),
        SimpleNamespace(
            PackageMeasureType="WEIGHT", PackageMeasureTextMetric="0.33 кг"
        ),
    ]
    assert get_weight(measurements) == 10.0  # type: ignore


def test_get_child_items_no_input():
    assert get_child_items([]) == []


def test_get_child_items_with_input():
    child_items = [
        SimpleNamespace(
            Quantity=10,
            ItemNo="70299474",
            ProductName="БЕСТО",
            ProductTypeName="каркас",
            ItemMeasureReferenceTextMetric=None,
            ValidDesignText=None,
            RetailItemCommPackageMeasureList=SimpleNamespace(
                RetailItemCommPackageMeasure=[
                    SimpleNamespace(
                        PackageMeasureType="WEIGHT", PackageMeasureTextMetric="17.95 кг"
                    )
                ]
            ),
        ),
        SimpleNamespace(
            Quantity=4,
            ItemNo="70299443",
            ProductName="БЕСТО",
            ProductTypeName="нажимные плавно закрывающиеся петли",
            ItemMeasureReferenceTextMetric=None,
            ValidDesignText=None,
            RetailItemCommPackageMeasureList=SimpleNamespace(
                RetailItemCommPackageMeasure=[
                    SimpleNamespace(
                        PackageMeasureType="WEIGHT", PackageMeasureTextMetric="13.19 кг"
                    )
                ]
            ),
        ),
    ]
    exp_result = [
        ChildItemDict(
            item_code="70299474", item_name="БЕСТО, Каркас", weight=17.95, qty=10
        ),
        ChildItemDict(
            item_code="70299443",
            item_name="БЕСТО, Нажимные плавно закрывающиеся петли",
            weight=13.19,
            qty=4,
        ),
    ]
    assert get_child_items(child_items) == exp_result  # type: ignore


def test_get_price_no_input():
    assert get_price([]) == 0


def test_get_price_not_list_zero():
    assert get_price(SimpleNamespace(Price=0)) == 0  # type: ignore


def test_get_price_not_list_not_zero():
    assert get_price(SimpleNamespace(Price=10)) == 10  # type: ignore


def test_get_price_list():
    assert get_price([SimpleNamespace(Price=5), SimpleNamespace(Price=20)]) == 5  # type: ignore


@pytest.mark.parametrize(
    ("item_code", "is_combination", "exp_res"),
    (
        ("11111111", False, f"/p/-11111111"),
        ("11111111", True, f"/p/-s11111111"),
    ),
)
def test_get_url(item_code: str, is_combination: bool, exp_res: str):
    assert (
        get_url(item_code, is_combination)
        == f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}{exp_res}"
    )


def test_get_category_name_and_url_no_category():
    assert get_category_name_and_url(
        [SimpleNamespace(CatalogElementList=SimpleNamespace(CatalogElement=[]))]  # type: ignore
    ) == (None, None)


@pytest.mark.parametrize(("name", "id"), (("value", {}), ({}, "value"), ({}, {})))
def test_get_category_name_and_url_name_or_id_is_dict(
    name: str | dict[Any, Any], id: str | dict[Any, Any]
):
    assert get_category_name_and_url(
        [  # type: ignore
            SimpleNamespace(
                CatalogElementList=SimpleNamespace(
                    CatalogElement=SimpleNamespace(
                        CatalogElementName=name, CatalogElementId=id
                    )
                )
            )
        ]
    ) == (None, None)


def test_get_category_name_and_url_passes():
    catalogs_first_el = [
        SimpleNamespace(
            CatalogElementList=SimpleNamespace(
                CatalogElement=SimpleNamespace(
                    CatalogElementName="name", CatalogElementId="id"
                )
            )
        )
    ]
    exp_res = (
        "name",
        f"{Constants.BASE_URL}/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/cat/-id",
    )
    assert get_category_name_and_url(catalogs_first_el) == exp_res  # type: ignore
    catalogs_second_el = [SimpleNamespace()] + catalogs_first_el
    assert get_category_name_and_url(catalogs_second_el) == exp_res  # type: ignore


test_data: tuple[dict[str, Any], ...] = (
    {
        "name": "default",
        "response": {
            "ItemNo": {"$": 30379118},
            "ItemNoGlobal": {"$": 40346924},
            "ItemType": {"$": "ART"},
            "ProductName": {"$": "КАЛЛАКС"},
            "ProductTypeName": {"$": "Стеллаж"},
            "ValidDesignText": {"$": "серый, под дерево"},
            "OnlineSellable": {"$": True},
            "BreathTakingItem": {"$": False},
            "ItemUnitCode": {"$": "PIECES"},
            "ItemNumberOfPackages": {"$": 1},
            "AssemblyCode": {"$": "Y"},
            "DesignerNameComm": {"$": "Tord Björklund"},
            "PriceUnitTextMetric": {},
            "GlobalisationContext": {
                "LanguageCodeIso": {"$": "ru"},
                "CountryCodeIso": {"$": "ru"},
            },
            "ClassUnitKey": {
                "ClassType": {"$": "GR"},
                "ClassUnitType": {"$": "RU"},
                "ClassUnitCode": {"$": "RU"},
            },
            "RetailItemCommPriceList": {
                "RetailItemCommPrice": {
                    "RetailPriceType": {"$": "RegularSalesUnitPrice"},
                    "Price": {"$": 7999},
                    "PriceExclTax": {"$": 6665.83},
                    "CurrencyCode": {"$": "RUB"},
                }
            },
            "RetailItemImageList": {
                "RetailItemImage": [
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S1"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__0494558_PE627165_S1.JPG"
                        },
                        "ImageWidth": {"$": 40},
                        "ImageHeight": {"$": 40},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S2"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__0494558_PE627165_S2.JPG"
                        },
                        "ImageWidth": {"$": 110},
                        "ImageHeight": {"$": 110},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__0494558_PE627165_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0494558_PE627165_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0494558_PE627165_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "PRICE TAG"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__13077.jpg"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "LINE DRAWING"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__0494559_PE627164_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0494559_PE627164_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0494559_PE627164_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz__0545555_PE655490_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0545555_PE655490_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/kallaks-stellaz-seryj__0545555_PE655490_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                ]
            },
            "GPRCommSelectionCriteriaSelectionList": {
                "GPRCommSelectionCriteriaSelection": [
                    {
                        "SelectionCriteriaCode": {"$": "COLOUR"},
                        "SelectionCriteriaName": {"$": "цвет"},
                        "SelectionCriteriaValue": {"$": "серый/под дерево"},
                    },
                    {
                        "SelectionCriteriaCode": {"$": "SIZE"},
                        "SelectionCriteriaName": {"$": "размеры"},
                        "SelectionCriteriaValue": {"$": "77x147 см"},
                    },
                ]
            },
            "AttributeGroupList": {
                "AttributeGroup": {
                    "GroupName": {"$": "SEO"},
                    "AttributeList": {
                        "Attribute": {
                            "Name": {"$": "DESCRIPTION"},
                            "Value": {
                                "$": "IKEA - КАЛЛАКС, Стеллаж, серый/под дерево , Можно использовать для разделения комнаты.Можно установить вертикально или горизонтально и использовать как стеллаж или сервант."
                            },
                        }
                    },
                }
            },
            "RetailItemCareInstructionList": {
                "RetailItemCareInstruction": {
                    "SortNo": {"$": 1},
                    "RetailItemCareInstructionTextList": {
                        "RetailItemCareInstructionText": [
                            {
                                "CareInstructionText": {
                                    "$": "Протирать мягкой влажной тканью, при необходимости можно использовать слабый мыльный раствор."
                                },
                                "SortNo": {"$": 1},
                            },
                            {
                                "CareInstructionText": {
                                    "$": "Вытирать чистой сухой тканью."
                                },
                                "SortNo": {"$": 2},
                            },
                        ]
                    },
                }
            },
            "RetailItemCustomerBenefitList": {
                "RetailItemCustomerBenefit": [
                    {
                        "CustomerBenefitText": {
                            "$": "Можно использовать для разделения комнаты."
                        },
                        "SortNo": {"$": 1},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Можно установить вертикально или горизонтально и использовать как стеллаж или сервант."
                        },
                        "SortNo": {"$": 2},
                    },
                ]
            },
            "RetailItemCustomerEnvironmentList": {
                "RetailItemCustomerEnvironment": {
                    "SortNo": {"$": 1},
                    "RetailItemEnvironmentTextList": {
                        "RetailItemEnvironmentText": [
                            {
                                "EnvironmentText": {
                                    "$": "Используя в этом товаре щит из ДВП и ДСП с сотовидным бумажным наполнителем, мы расходуем меньше древесины, а значит, бережнее относимся к ресурсам планеты."
                                },
                                "SortNo": {"$": 1},
                            },
                            {
                                "EnvironmentText": {
                                    "$": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы."
                                },
                                "SortNo": {"$": 2},
                            },
                        ]
                    },
                }
            },
            "RetailItemGoodToKnowList": {
                "RetailItemGoodToKnow": [
                    {
                        "GoodToKnowTypeNameEn": {"$": "Warning"},
                        "GoodToKnowText": {
                            "$": "Эту мебель необходимо крепить к стене с помощью прилагаемого стенного крепежа."
                        },
                        "SortNo": {"$": 1},
                        "GoodToKnowHeader": {"$": "Безопасность и соответствие:"},
                    },
                    {
                        "GoodToKnowTypeNameEn": {"$": "Compl. assembly information"},
                        "GoodToKnowText": {
                            "$": "Для разных стен требуются различные крепежные приспособления. Подберите подходящие для ваших стен шурупы, дюбели, саморезы и т. п. (не прилагаются)."
                        },
                        "SortNo": {"$": 2},
                        "GoodToKnowHeader": {"$": "Сборка и установка"},
                    },
                    {
                        "GoodToKnowTypeNameEn": {"$": "Compl. assembly information"},
                        "GoodToKnowText": {
                            "$": "Для сборки этой мебели требуются два человека."
                        },
                        "SortNo": {"$": 3},
                        "GoodToKnowHeader": {"$": "Сборка и установка"},
                    },
                    {
                        "GoodToKnowTypeNameEn": {"$": "May be completed"},
                        "GoodToKnowText": {
                            "$": "Можно дополнить вставкой КАЛЛАКС, продается отдельно."
                        },
                        "SortNo": {"$": 4},
                        "GoodToKnowHeader": {"$": "Для готового решения"},
                    },
                ]
            },
            "RetailItemCustomerMaterialList": {
                "RetailItemCustomerMaterial": {
                    "SortNo": {"$": 1},
                    "RetailItemPartMaterialList": {
                        "RetailItemPartMaterial": {
                            "MaterialText": {
                                "$": "ДСП, ДВП, Бумажная пленка, Акриловая краска с тиснением и печатным рисунком, Сотовидный бумажный наполнитель (мин. 70 % переработанного материала), Пластиковая окантовка, Пластмасса АБС"
                            },
                            "SortNo": {"$": 1},
                        }
                    },
                }
            },
            "RetailItemCommPackageMeasureList": {
                "RetailItemCommPackageMeasure": [
                    {
                        "PackageMeasureType": {"$": "WIDTH"},
                        "PackageMeasureTextMetric": {"$": "41 см"},
                        "PackageMeasureTextImperial": {"$": "16 дюйм"},
                        "SortNo": {"$": 1},
                        "ConsumerPackNumber": {"$": 1},
                    },
                    {
                        "PackageMeasureType": {"$": "HEIGHT"},
                        "PackageMeasureTextMetric": {"$": "16 см"},
                        "PackageMeasureTextImperial": {"$": "6 ¼ дюйм"},
                        "SortNo": {"$": 1},
                        "ConsumerPackNumber": {"$": 1},
                    },
                    {
                        "PackageMeasureType": {"$": "LENGTH"},
                        "PackageMeasureTextMetric": {"$": "149 см"},
                        "PackageMeasureTextImperial": {"$": "58 ¾ дюйм"},
                        "SortNo": {"$": 1},
                        "ConsumerPackNumber": {"$": 1},
                    },
                    {
                        "PackageMeasureType": {"$": "WEIGHT"},
                        "PackageMeasureTextMetric": {"$": "21.28 кг"},
                        "PackageMeasureTextImperial": {"$": "46 фнт 15 унц"},
                        "SortNo": {"$": 1},
                        "ConsumerPackNumber": {"$": 1},
                    },
                ]
            },
            "RetailItemCommMeasureList": {
                "RetailItemCommMeasure": [
                    {
                        "ItemMeasureType": {"$": "Width"},
                        "ItemMeasureTypeName": {"$": "Ширина"},
                        "ItemMeasureTextMetric": {"$": "77 см"},
                        "ItemMeasureTextImperial": {"$": "30 3/8 дюйм"},
                        "SortNo": {"$": 1},
                    },
                    {
                        "ItemMeasureType": {"$": "Depth"},
                        "ItemMeasureTypeName": {"$": "Глубина"},
                        "ItemMeasureTextMetric": {"$": "39 см"},
                        "ItemMeasureTextImperial": {"$": "15 3/8 дюйм"},
                        "SortNo": {"$": 2},
                    },
                    {
                        "ItemMeasureType": {"$": "Height"},
                        "ItemMeasureTypeName": {"$": "Высота"},
                        "ItemMeasureTextMetric": {"$": "147 см"},
                        "ItemMeasureTextImperial": {"$": "57 7/8 дюйм"},
                        "SortNo": {"$": 3},
                    },
                    {
                        "ItemMeasureType": {"$": "Max. load/shelf"},
                        "ItemMeasureTypeName": {"$": "Макс нагрузка на полку"},
                        "ItemMeasureTextMetric": {"$": "13 кг"},
                        "ItemMeasureTextImperial": {"$": "29 фнт"},
                        "SortNo": {"$": 4},
                    },
                ]
            },
            "CatalogRefList": {
                "CatalogRef": [
                    {
                        "Catalog": {
                            "CatalogId": {"$": "genericproducts"},
                            "CatalogName": {"$": "Товары"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/genericproducts"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {"$": 27285},
                                "CatalogElementType": {"$": "GENERIC PRODUCT"},
                                "CatalogElementName": {"$": "Каллакс"},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/genericproducts/27285"
                                },
                            }
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "series"},
                            "CatalogName": {"$": "Серии"},
                            "CatalogUrl": {"$": "/retail/iows/ru/ru/catalog/series"},
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {"$": 27534},
                                "CatalogElementType": {"$": "TOP CATEGORY"},
                                "CatalogElementName": {"$": "КАЛЛАКС серия"},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/series/27534"
                                },
                            }
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "departments"},
                            "CatalogName": {"$": "Отделы"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/departments"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": [
                                {
                                    "CatalogElementId": {"$": 10382},
                                    "CatalogElementType": {"$": "SUB CATEGORY"},
                                    "CatalogElementName": {"$": "Книжные шкафы"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/departments/living_room/10382"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 10412},
                                    "CatalogElementType": {"$": "CHAPTER"},
                                    "CatalogElementName": {"$": "Серванты и буфеты"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/departments/dining/10412"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 11465},
                                    "CatalogElementType": {"$": "SUB CATEGORY"},
                                    "CatalogElementName": {"$": "Стеллажи"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/departments/living_room/11465"
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "functional"},
                            "CatalogName": {"$": "Функциональный"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/functional"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": [
                                {
                                    "CatalogElementId": {"$": 10382},
                                    "CatalogElementType": {"$": "SUB CATEGORY"},
                                    "CatalogElementName": {"$": "Книжные шкафы"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/functional/10364/10382"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 11465},
                                    "CatalogElementType": {"$": "SUB CATEGORY"},
                                    "CatalogElementName": {"$": "Стеллажи"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/functional/10364/11465"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 10412},
                                    "CatalogElementType": {"$": "CHAPTER"},
                                    "CatalogElementName": {"$": "Серванты и буфеты"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/functional/10364/10412"
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "seasonal"},
                            "CatalogName": {"$": "Сезонный"},
                            "CatalogUrl": {"$": "/retail/iows/ru/ru/catalog/seasonal"},
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {"$": 11465},
                                "CatalogElementType": {"$": "SUB CATEGORY"},
                                "CatalogElementName": {"$": "Стеллажи"},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/seasonal/back_to_college/11465"
                                },
                            }
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "planner"},
                            "CatalogName": {"$": "Планировщик"},
                            "CatalogUrl": {"$": "/retail/iows/ru/ru/catalog/planner"},
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {},
                                "CatalogElementType": {"$": "TOP CATEGORY"},
                                "CatalogElementName": {},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/planner/"
                                },
                            }
                        },
                    },
                ]
            },
            "PriceUnitTextMetricEn": {},
            "PriceUnitTextImperialEn": {},
            "RetailItemCommAttachmentList": {
                "RetailItemCommAttachment": {
                    "AttachmentType": {"$": "ASSEMBLY_INSTRUCTION"},
                    "AttachmentUrl": {
                        "$": "/ru/ru/assembly_instructions/kallaks-stellaz__AA-1055145-8_pub.pdf"
                    },
                    "SortNo": {"$": 1},
                }
            },
            "ItemMeasureReferenceTextMetric": {"$": "77x147 см"},
            "ItemMeasureReferenceTextImperial": {"$": "30 3/8x57 7/8 дюйм"},
            "CatalogElementRelationList": {
                "CatalogElementRelation": {
                    "CatalogElementRelationType": {"$": "X-SELL"},
                    "CatalogElementRelationSemantic": {"$": "MAY_BE_COMPLETED_WITH"},
                    "CatalogElementId": {"$": 60376420},
                    "CatalogElementType": {"$": "ART"},
                    "CatalogElementName": {"$": "ДРЁНА"},
                    "CatalogElementUrl": {
                        "$": "/retail/iows/ru/ru/catalog/items/art,60376420"
                    },
                    "SortRelevanceList": {
                        "SortRelevance": {
                            "SortNo": {"$": 6},
                            "SortType": {"$": "RELEVANCE"},
                        }
                    },
                }
            },
            "RetailItemFullLengthTextList": {"RetailItemFullLengthText": {}},
            "RetailItemFilterAttributeList": {
                "RetailItemFilterAttribute": [
                    {
                        "FilterAttributeType": {"$": "Colour"},
                        "FilterAttributeTypeName": {"$": "Цвет"},
                        "FilterAttributeValueList": {
                            "FilterAttributeValue": {
                                "FilterAttributeValueId": {"$": 10028},
                                "FilterAttributeValueName": {"$": "серый"},
                            }
                        },
                    },
                    {
                        "FilterAttributeType": {"$": "Material"},
                        "FilterAttributeTypeName": {"$": "Материал"},
                        "FilterAttributeValueList": {
                            "FilterAttributeValue": {
                                "FilterAttributeValueId": {"$": 47349},
                                "FilterAttributeValueName": {
                                    "$": "Древесина (в т. ч. доска)"
                                },
                            }
                        },
                    },
                    {
                        "FilterAttributeType": {"$": "Number of seats"},
                        "FilterAttributeTypeName": {"$": "Свойства"},
                        "FilterAttributeValueList": {
                            "FilterAttributeValue": {
                                "FilterAttributeValueId": {"$": 53039},
                                "FilterAttributeValueName": {"$": "С полками"},
                            }
                        },
                    },
                    {
                        "FilterAttributeType": {"$": "Number of seats"},
                        "FilterAttributeTypeName": {"$": "Дверцы"},
                        "FilterAttributeValueList": {
                            "FilterAttributeValue": {
                                "FilterAttributeValueId": {"$": 47687},
                                "FilterAttributeValueName": {"$": "Без дверей"},
                            }
                        },
                    },
                ]
            },
            "@xmlns": {"$": "ikea.com/cem/iows/RetailItemCommunicationService/2.0/"},
        },
    },
    {
        "name": "combination",
        "response": {
            "ItemNo": {"$": 69435788},
            "ItemNoGlobal": {"$": 19421675},
            "ItemType": {"$": "SPR"},
            "ProductName": {"$": "БЕСТО"},
            "ProductTypeName": {"$": "Комбинация для хранения с дверцами"},
            "ValidDesignText": {"$": "белый, бьёркёвикен березовый шпон"},
            "NewsType": {"$": "ICON"},
            "OnlineSellable": {"$": True},
            "BreathTakingItem": {"$": False},
            "ItemUnitCode": {"$": "PIECES"},
            "ItemNumberOfPackages": {"$": 24},
            "AssemblyCode": {"$": "Y"},
            "DesignerNameComm": {},
            "PriceUnitTextMetric": {},
            "GlobalisationContext": {
                "LanguageCodeIso": {"$": "ru"},
                "CountryCodeIso": {"$": "ru"},
            },
            "ClassUnitKey": {
                "ClassType": {"$": "GR"},
                "ClassUnitType": {"$": "RU"},
                "ClassUnitCode": {"$": "RU"},
            },
            "RetailItemCommPriceList": {
                "RetailItemCommPrice": {
                    "RetailPriceType": {"$": "RegularSalesUnitPrice"},
                    "Price": {"$": 31800},
                    "PriceExclTax": {"$": 26500},
                    "CurrencyCode": {"$": "RUB"},
                }
            },
            "RetailItemImageList": {
                "RetailItemImage": [
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S1"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__0994361_PE821029_S1.JPG"
                        },
                        "ImageWidth": {"$": 40},
                        "ImageHeight": {"$": 40},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S2"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__0994361_PE821029_S2.JPG"
                        },
                        "ImageWidth": {"$": 110},
                        "ImageHeight": {"$": 110},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__0994361_PE821029_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0994361_PE821029_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0994361_PE821029_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 1},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__0999944_PE823959_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0999944_PE823959_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0999944_PE823959_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 2},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__1026859_PE834586_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__1026859_PE834586_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__1026859_PE834586_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 3},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S3"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami__0998425_PE823028_S3.JPG"
                        },
                        "ImageWidth": {"$": 250},
                        "ImageHeight": {"$": 250},
                        "SortNo": {"$": 4},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S4"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0998425_PE823028_S4.JPG"
                        },
                        "ImageWidth": {"$": 500},
                        "ImageHeight": {"$": 500},
                        "SortNo": {"$": 4},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                    {
                        "ImageUsage": {"$": "INTERNET"},
                        "ImageSize": {"$": "S5"},
                        "ImageUrl": {
                            "$": "/ru/ru/images/products/besto-kombinacia-dla-hranenia-s-dvercami-belyj__0998425_PE823028_S5.JPG"
                        },
                        "ImageWidth": {"$": 2000},
                        "ImageHeight": {"$": 2000},
                        "SortNo": {"$": 4},
                        "ImageType": {"$": "PICTURE SINGLE"},
                    },
                ]
            },
            "GPRCommSelectionCriteriaSelectionList": {
                "GPRCommSelectionCriteriaSelection": [
                    {
                        "SelectionCriteriaCode": {"$": "COLOUR"},
                        "SelectionCriteriaName": {"$": "цвет"},
                        "SelectionCriteriaValue": {
                            "$": "белый/бьёркёвикен березовый шпон"
                        },
                    },
                    {
                        "SelectionCriteriaCode": {"$": "SIZE"},
                        "SelectionCriteriaName": {"$": "размеры"},
                        "SelectionCriteriaValue": {"$": "120x42x193 см"},
                    },
                    {
                        "SelectionCriteriaCode": {"$": "00159"},
                        "SelectionCriteriaName": {"$": "ящик"},
                        "SelectionCriteriaValue": {"$": "-"},
                    },
                ]
            },
            "AttributeGroupList": {
                "AttributeGroup": {
                    "GroupName": {"$": "SEO"},
                    "AttributeList": {
                        "Attribute": {
                            "Name": {"$": "DESCRIPTION"},
                            "Value": {
                                "$": "IKEA - БЕСТО, Комбинация для хранения с дверцами, белый/бьёркёвикен березовый шпон, 120x42x193 см , Фасад БЬЁРКЁВИКЕН изготовлен из березового шпона, который придает каждой дверце непревзойденное качество и естественную красоту.Дверцы защищают содерж"
                            },
                        }
                    },
                }
            },
            "RetailItemCareInstructionList": {
                "RetailItemCareInstruction": [
                    {
                        "ProductTypeText": {"$": "Дверь"},
                        "SortNo": {"$": 1},
                        "RetailItemCareInstructionTextList": {
                            "RetailItemCareInstructionText": [
                                {
                                    "CareInstructionText": {
                                        "$": "Протирать влажной тканью."
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "CareInstructionText": {
                                        "$": "Вытирать чистой сухой тканью."
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Каркас/полка"},
                        "SortNo": {"$": 2},
                        "RetailItemCareInstructionTextList": {
                            "RetailItemCareInstructionText": [
                                {
                                    "CareInstructionText": {
                                        "$": "Протирать влажной тканью."
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "CareInstructionText": {
                                        "$": "Вытирать чистой сухой тканью."
                                    },
                                    "SortNo": {"$": 2},
                                },
                                {
                                    "CareInstructionText": {
                                        "$": "Регулярно проверяйте все крепления и подтягивайте их при необходимости."
                                    },
                                    "SortNo": {"$": 3},
                                },
                            ]
                        },
                    },
                ]
            },
            "RetailItemCustomerBenefitList": {
                "RetailItemCustomerBenefit": [
                    {
                        "CustomerBenefitText": {
                            "$": "Фасад БЬЁРКЁВИКЕН изготовлен из березового шпона, который придает каждой дверце непревзойденное качество и естественную красоту."
                        },
                        "SortNo": {"$": 1},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Дверцы защищают содержимое и выполняют декоративную функцию. Выберите дверцы, подходящие к интерьеру Вашего дома."
                        },
                        "SortNo": {"$": 2},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Съемные полки позволяют регулировать пространство."
                        },
                        "SortNo": {"$": 3},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Вы можете использовать нажимной механизм или устройство для плавного закрывания. В первом варианте для открывания дверцы достаточно слегка нажать на нее. А во втором – гарантировано плавное и бесшумное закрывание."
                        },
                        "SortNo": {"$": 4},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Конструкция петель позволяет отрегулировать и выровнять дверцу по вертикали и по горизонтали."
                        },
                        "SortNo": {"$": 5},
                    },
                    {
                        "CustomerBenefitText": {
                            "$": "Организуйте и оптимизируйте систему для хранения БЕСТО, используя подходящие коробки и вставки."
                        },
                        "SortNo": {"$": 6},
                    },
                ]
            },
            "RetailItemCustomerEnvironmentList": {
                "RetailItemCustomerEnvironment": [
                    {
                        "ProductTypeText": {"$": "Каркас"},
                        "SortNo": {"$": 1},
                        "RetailItemEnvironmentTextList": {
                            "RetailItemEnvironmentText": [
                                {
                                    "EnvironmentText": {
                                        "$": "Используя в этом товаре щит из ДВП и ДСП с сотовидным бумажным наполнителем, мы расходуем меньше древесины, а значит, бережнее относимся к ресурсам планеты."
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "EnvironmentText": {
                                        "$": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы."
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Полка"},
                        "SortNo": {"$": 2},
                        "RetailItemEnvironmentTextList": {
                            "RetailItemEnvironmentText": [
                                {
                                    "EnvironmentText": {
                                        "$": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы."
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "EnvironmentText": {
                                        "$": "Используя в ДСП этого товара отходы деревообрабатывающего производства, мы находим применение не только для ствола, а для всего дерева. Это позволяет нам бережнее расходовать ресурсы."
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Дверь"},
                        "SortNo": {"$": 3},
                        "RetailItemEnvironmentTextList": {
                            "RetailItemEnvironmentText": [
                                {
                                    "EnvironmentText": {
                                        "$": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы."
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "EnvironmentText": {
                                        "$": "Используя для изготовления этого товара ДСП с верхним слоем дерева вместо массива, мы используем меньше природного сырья, что позволяет эффективно расходовать ресурсы."
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                ]
            },
            "RetailItemGoodToKnowList": {
                "RetailItemGoodToKnow": [
                    {
                        "GoodToKnowTypeNameEn": {"$": "Warning"},
                        "GoodToKnowText": {
                            "$": "Эту мебель необходимо крепить к стене с помощью прилагаемого стенного крепежа."
                        },
                        "SortNo": {"$": 1},
                        "GoodToKnowHeader": {"$": "Безопасность и соответствие:"},
                    },
                    {
                        "GoodToKnowTypeNameEn": {"$": "Compl. assembly information"},
                        "GoodToKnowText": {
                            "$": "Для разных стен требуются различные крепежные приспособления. Подберите подходящие для ваших стен шурупы, дюбели, саморезы и т. п. (не прилагаются)."
                        },
                        "SortNo": {"$": 2},
                        "GoodToKnowHeader": {"$": "Сборка и установка"},
                    },
                    {
                        "GoodToKnowTypeNameEn": {"$": "Purchase-/Other information"},
                        "GoodToKnowText": {
                            "$": "Если вы выберете функцию плавного закрывания, рекомендуем дополнить фасады ручками, чтобы открывать ящики/шкафы было удобнее."
                        },
                        "SortNo": {"$": 3},
                        "GoodToKnowHeader": {"$": "Дополнительная информация"},
                    },
                ]
            },
            "RetailItemCustomerMaterialList": {
                "RetailItemCustomerMaterial": [
                    {
                        "ProductTypeText": {"$": "Каркас"},
                        "SortNo": {"$": 1},
                        "RetailItemPartMaterialList": {
                            "RetailItemPartMaterial": [
                                {
                                    "PartText": {"$": "Панель:"},
                                    "MaterialText": {
                                        "$": "ДСП, Сотовидный бумажный наполнитель (100 % переработанного материала), ДВП, Бумажная пленка, Пластиковая окантовка, Пластиковая окантовка, Бумажная пленка"
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "PartText": {"$": "Задняя панель:"},
                                    "MaterialText": {
                                        "$": "ДВП, Бумажная пленка, Полимерная пленка"
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Полка"},
                        "SortNo": {"$": 2},
                        "RetailItemPartMaterialList": {
                            "RetailItemPartMaterial": {
                                "MaterialText": {
                                    "$": "ДСП, Бумажная пленка, Пластиковая окантовка, Пластиковая окантовка, Бумажная пленка"
                                },
                                "SortNo": {"$": 1},
                            }
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Дверь"},
                        "SortNo": {"$": 3},
                        "RetailItemPartMaterialList": {
                            "RetailItemPartMaterial": {
                                "MaterialText": {
                                    "$": "ДВП, Березовый шпон, Прозрачный акриловый лак"
                                },
                                "SortNo": {"$": 1},
                            }
                        },
                    },
                    {
                        "ProductTypeText": {"$": "Нажимные плавно закрывающиеся петли"},
                        "SortNo": {"$": 4},
                        "RetailItemPartMaterialList": {
                            "RetailItemPartMaterial": [
                                {
                                    "PartText": {"$": "Металлическая часть:"},
                                    "MaterialText": {"$": "Сталь, Никелирование"},
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "PartText": {"$": "Пластмассовые части:"},
                                    "MaterialText": {"$": "Ацеталь пластик"},
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                ]
            },
            "RetailItemCommMeasureList": {
                "RetailItemCommMeasure": [
                    {
                        "ItemMeasureType": {"$": "Width"},
                        "ItemMeasureTypeName": {"$": "Ширина"},
                        "ItemMeasureTextMetric": {"$": "120 см"},
                        "ItemMeasureTextImperial": {"$": "47 1/4 дюйм"},
                        "SortNo": {"$": 1},
                    },
                    {
                        "ItemMeasureType": {"$": "Depth"},
                        "ItemMeasureTypeName": {"$": "Глубина"},
                        "ItemMeasureTextMetric": {"$": "42 см"},
                        "ItemMeasureTextImperial": {"$": "16 1/2 дюйм"},
                        "SortNo": {"$": 2},
                    },
                    {
                        "ItemMeasureType": {"$": "Height"},
                        "ItemMeasureTypeName": {"$": "Высота"},
                        "ItemMeasureTextMetric": {"$": "193 см"},
                        "ItemMeasureTextImperial": {"$": "76 дюйм"},
                        "SortNo": {"$": 3},
                    },
                    {
                        "ItemMeasureType": {"$": "Max. load/shelf"},
                        "ItemMeasureTypeName": {"$": "Макс нагрузка на полку"},
                        "ItemMeasureTextMetric": {"$": "20 кг"},
                        "ItemMeasureTextImperial": {"$": "44 фнт"},
                        "SortNo": {"$": 4},
                    },
                ]
            },
            "RetailItemCommChildList": {
                "RetailItemCommChild": [
                    {
                        "Quantity": {"$": 2},
                        "ItemNo": {"$": "00299340"},
                        "ItemNoGlobal": {"$": "00245842"},
                        "ItemType": {"$": "ART"},
                        "ItemUrl": {
                            "$": "/retail/iows/ru/ru/catalog/items/art,00245842"
                        },
                        "ProductName": {"$": "БЕСТО"},
                        "ProductTypeName": {"$": "каркас"},
                        "ItemNumberOfPackages": {"$": 1},
                        "RetailItemCommPackageMeasureList": {
                            "RetailItemCommPackageMeasure": [
                                {
                                    "PackageMeasureType": {"$": "WIDTH"},
                                    "PackageMeasureTextMetric": {"$": "41 см"},
                                    "PackageMeasureTextImperial": {"$": "16 ¼ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "HEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "8 см"},
                                    "PackageMeasureTextImperial": {"$": "3 дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "LENGTH"},
                                    "PackageMeasureTextMetric": {"$": "195 см"},
                                    "PackageMeasureTextImperial": {"$": "76 ¾ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "WEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "17.95 кг"},
                                    "PackageMeasureTextImperial": {"$": "39 фнт 9 унц"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                            ]
                        },
                        "RetailItemCommAttachmentList": {
                            "RetailItemCommAttachment": [
                                {
                                    "AttachmentType": {"$": "ASSEMBLY_INSTRUCTION"},
                                    "AttachmentUrl": {
                                        "$": "/ru/ru/assembly_instructions/besto-karkas__AA-1272094-7_pub.pdf"
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "AttachmentType": {"$": "MANUAL"},
                                    "AttachmentUrl": {
                                        "$": "/ru/ru/manuals/besto-karkas__AA-2205802-3_pub.pdf"
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                    {
                        "Quantity": {"$": 6},
                        "ItemNo": {"$": "00383881"},
                        "ItemNoGlobal": {"$": 80261258},
                        "ItemType": {"$": "ART"},
                        "ItemUrl": {
                            "$": "/retail/iows/ru/ru/catalog/items/art,80261258"
                        },
                        "ProductName": {"$": "БЕСТО"},
                        "ProductTypeName": {"$": "нажимные плавно закрывающиеся петли"},
                        "ItemNumberOfPackages": {"$": 1},
                        "RetailItemCommPackageMeasureList": {
                            "RetailItemCommPackageMeasure": [
                                {
                                    "PackageMeasureType": {"$": "WIDTH"},
                                    "PackageMeasureTextMetric": {"$": "20 см"},
                                    "PackageMeasureTextImperial": {"$": "7 ¾ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "HEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "3 см"},
                                    "PackageMeasureTextImperial": {"$": "1 дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "LENGTH"},
                                    "PackageMeasureTextMetric": {"$": "25 см"},
                                    "PackageMeasureTextImperial": {"$": "9 ¾ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "WEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "0.26 кг"},
                                    "PackageMeasureTextImperial": {"$": "9 унц"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                            ]
                        },
                        "RetailItemCommAttachmentList": {
                            "RetailItemCommAttachment": {
                                "AttachmentType": {"$": "ASSEMBLY_INSTRUCTION"},
                                "AttachmentUrl": {
                                    "$": "/ru/ru/assembly_instructions/besto-nazimnye-plavno-zakryvausiesa-petli__AA-2235776-1_pub.pdf"
                                },
                                "SortNo": {"$": 1},
                            }
                        },
                    },
                    {
                        "Quantity": {"$": 6},
                        "ItemNo": {"$": 40490959},
                        "ItemNoGlobal": {"$": 80490957},
                        "ItemType": {"$": "ART"},
                        "ItemUrl": {
                            "$": "/retail/iows/ru/ru/catalog/items/art,80490957"
                        },
                        "ProductName": {"$": "БЬЁРКЁВИКЕН"},
                        "ProductTypeName": {"$": "дверь"},
                        "ItemNumberOfPackages": {"$": 1},
                        "RetailItemCommPackageMeasureList": {
                            "RetailItemCommPackageMeasure": [
                                {
                                    "PackageMeasureType": {"$": "WIDTH"},
                                    "PackageMeasureTextMetric": {"$": "62 см"},
                                    "PackageMeasureTextImperial": {"$": "24 ¼ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "HEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "2 см"},
                                    "PackageMeasureTextImperial": {"$": "¾ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "LENGTH"},
                                    "PackageMeasureTextMetric": {"$": "74 см"},
                                    "PackageMeasureTextImperial": {"$": "29 ¼ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "WEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "5.23 кг"},
                                    "PackageMeasureTextImperial": {"$": "11 фнт 8 унц"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                            ]
                        },
                        "RetailItemCommAttachmentList": {
                            "RetailItemCommAttachment": {
                                "AttachmentType": {"$": "MANUAL"},
                                "AttachmentUrl": {
                                    "$": "/ru/ru/manuals/b-erkeviken-dver-__AA-2205802-3_pub.pdf"
                                },
                                "SortNo": {"$": 1},
                            }
                        },
                    },
                    {
                        "Quantity": {"$": 10},
                        "ItemNo": {"$": 70299474},
                        "ItemNoGlobal": {"$": "00295554"},
                        "ItemType": {"$": "ART"},
                        "ItemUrl": {
                            "$": "/retail/iows/ru/ru/catalog/items/art,00295554"
                        },
                        "ProductName": {"$": "БЕСТО"},
                        "ProductTypeName": {"$": "полка"},
                        "ItemNumberOfPackages": {"$": 1},
                        "RetailItemCommPackageMeasureList": {
                            "RetailItemCommPackageMeasure": [
                                {
                                    "PackageMeasureType": {"$": "WIDTH"},
                                    "PackageMeasureTextMetric": {"$": "36 см"},
                                    "PackageMeasureTextImperial": {"$": "14 дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "HEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "2 см"},
                                    "PackageMeasureTextImperial": {"$": "¾ дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "LENGTH"},
                                    "PackageMeasureTextMetric": {"$": "59 см"},
                                    "PackageMeasureTextImperial": {"$": "23 дюйм"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                                {
                                    "PackageMeasureType": {"$": "WEIGHT"},
                                    "PackageMeasureTextMetric": {"$": "1.50 кг"},
                                    "PackageMeasureTextImperial": {"$": "3 фнт 5 унц"},
                                    "SortNo": {"$": 1},
                                    "ConsumerPackNumber": {"$": 1},
                                },
                            ]
                        },
                        "RetailItemCommAttachmentList": {
                            "RetailItemCommAttachment": [
                                {
                                    "AttachmentType": {"$": "ASSEMBLY_INSTRUCTION"},
                                    "AttachmentUrl": {
                                        "$": "/ru/ru/assembly_instructions/besto-polka__AA-1227320-2_pub.pdf"
                                    },
                                    "SortNo": {"$": 1},
                                },
                                {
                                    "AttachmentType": {"$": "MANUAL"},
                                    "AttachmentUrl": {
                                        "$": "/ru/ru/manuals/besto-polka__AA-2205802-3_pub.pdf"
                                    },
                                    "SortNo": {"$": 2},
                                },
                            ]
                        },
                    },
                ]
            },
            "CatalogRefList": {
                "CatalogRef": [
                    {
                        "Catalog": {
                            "CatalogId": {"$": "genericproducts"},
                            "CatalogName": {"$": "Товары"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/genericproducts"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {"$": 31559},
                                "CatalogElementType": {"$": "GENERIC PRODUCT"},
                                "CatalogElementName": {"$": "Бесто"},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/genericproducts/31559"
                                },
                            }
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "departments"},
                            "CatalogName": {"$": "Отделы"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/departments"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": [
                                {
                                    "CatalogElementId": {"$": 12150},
                                    "CatalogElementType": {
                                        "$": "CATEGORY SYSTEM CHAPTER"
                                    },
                                    "CatalogElementName": {"$": "Комбинации БЕСТО"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/departments/living_room/12150"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 55023},
                                    "CatalogElementType": {
                                        "$": "CATEGORY SYSTEM CHAPTER"
                                    },
                                    "CatalogElementName": {
                                        "$": "БЕСТО комбинации для хранения"
                                    },
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/departments/living_room/55023"
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "functional"},
                            "CatalogName": {"$": "Функциональный"},
                            "CatalogUrl": {
                                "$": "/retail/iows/ru/ru/catalog/functional"
                            },
                        },
                        "CatalogElementList": {
                            "CatalogElement": [
                                {
                                    "CatalogElementId": {"$": 12150},
                                    "CatalogElementType": {
                                        "$": "CATEGORY SYSTEM CHAPTER"
                                    },
                                    "CatalogElementName": {"$": "Комбинации БЕСТО"},
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/functional/10364/12150"
                                    },
                                },
                                {
                                    "CatalogElementId": {"$": 55023},
                                    "CatalogElementType": {
                                        "$": "CATEGORY SYSTEM CHAPTER"
                                    },
                                    "CatalogElementName": {
                                        "$": "БЕСТО комбинации для хранения"
                                    },
                                    "CatalogElementUrl": {
                                        "$": "/retail/iows/ru/ru/catalog/functional/10364/55023"
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "Catalog": {
                            "CatalogId": {"$": "planner"},
                            "CatalogName": {"$": "Планировщик"},
                            "CatalogUrl": {"$": "/retail/iows/ru/ru/catalog/planner"},
                        },
                        "CatalogElementList": {
                            "CatalogElement": {
                                "CatalogElementId": {"$": "BESTA_planner"},
                                "CatalogElementType": {"$": "TOP CATEGORY"},
                                "CatalogElementName": {"$": "BESTA_planner"},
                                "CatalogElementUrl": {
                                    "$": "/retail/iows/ru/ru/catalog/planner/BESTA_planner"
                                },
                            }
                        },
                    },
                ]
            },
            "PriceUnitTextMetricEn": {},
            "PriceUnitTextImperialEn": {},
            "ItemMeasureReferenceTextMetric": {"$": "120x42x193 см"},
            "ItemMeasureReferenceTextImperial": {"$": "47 1/4x16 1/2x76 дюйм"},
            "CatalogElementRelationList": {},
            "RetailItemCustomerBenefitSummaryText": {
                "$": "Все, что вам нужно для хранения вещей и поддержания порядка в доме. Выберите готовую комбинацию или создайте собственную, ориентируясь на свои потребности и стиль. Эта — лишь один вариант из множества возможностей."
            },
            "RetailItemFullLengthTextList": {"RetailItemFullLengthText": {}},
            "@xmlns": {"$": "ikea.com/cem/iows/RetailItemCommunicationService/2.0/"},
        },
    },
)


@pytest.mark.parametrize("test_data_response", test_data)
def test_main(test_data_response: dict[str, Any]):
    main(test_data_response["response"])
