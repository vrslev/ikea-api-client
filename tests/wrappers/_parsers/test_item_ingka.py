from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.exceptions import ParsingError
from ikea_api.wrappers._parsers.item_ingka import (
    Constants,
    _parse_russian_product_name,
    get_child_items,
    get_image_url,
    get_localised_communication,
    get_name,
    get_weight,
    main,
)


def test_get_localised_communication_passes():
    Constants.LANGUAGE_CODE = "nolang"
    exp_res = SimpleNamespace(languageCode="nolang")
    communications = [
        SimpleNamespace(languageCode="ru"),
        SimpleNamespace(languageCode="en"),
        exp_res,
    ]
    assert get_localised_communication(communications) == exp_res  # type: ignore
    Constants.LANGUAGE_CODE = "ru"


def test_get_localised_communication_raises():
    Constants.LANGUAGE_CODE = "nolang"
    communications = [
        SimpleNamespace(languageCode="ru"),
        SimpleNamespace(languageCode="en"),
    ]
    with pytest.raises(
        ParsingError, match="Cannot find appropriate localized communication"
    ):
        get_localised_communication(communications)  # type: ignore
    Constants.LANGUAGE_CODE = "ru"


@pytest.mark.parametrize(
    ("input", "output"),
    (
        ("MARABOU", "MARABOU"),
        ("IKEA 365+ ИКЕА/365+", "ИКЕА/365+"),
        ("VINTER 2021 ВИНТЕР 2021", "ВИНТЕР 2021"),
        ("BESTÅ БЕСТО / EKET ЭКЕТ", "БЕСТО / ЭКЕТ"),
        ("BESTÅ", "BESTÅ"),
        ("BESTÅ БЕСТО", "БЕСТО"),
    ),
)
def test_parse_russian_product_name(input: str, output: str):
    assert _parse_russian_product_name(input) == output


@pytest.mark.parametrize(
    ("product_name", "product_type", "design", "measurements", "exp_result"),
    (
        (
            "EKET ЭКЕТ",
            "комбинация настенных шкафов",
            "белый/светло-зеленый",
            "175x25x70 см",
            "ЭКЕТ, Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
        ),
        (
            "KALLAX КАЛЛАКС",
            "стеллаж",
            "серый/под дерево",
            "77x147 см",
            "КАЛЛАКС, Стеллаж, серый/под дерево, 77x147 см",
        ),
        (
            "FENOMEN ФЕНОМЕН",
            "неароматическая формовая свеча, 5шт",
            "естественный",
            None,
            "ФЕНОМЕН, Неароматическая формовая свеча, 5шт, естественный",
        ),
        ("MARABOU", "шоколад Дайм", None, None, "MARABOU, Шоколад дайм"),
    ),
)
def test_get_name(
    product_name: str,
    product_type: str,
    design: str | None,
    measurements: str | None,
    exp_result: str,
):
    comm = SimpleNamespace(
        productName=product_name,
        productType=SimpleNamespace(name=product_type),
        validDesign=SimpleNamespace(text=design) if design else None,
        measurements=SimpleNamespace(
            referenceMeasurements=[SimpleNamespace(metric=measurements)]
        )
        if measurements
        else None,
    )

    assert get_name(comm) == exp_result  # type: ignore


def test_get_image_url_not_main_image():
    exp_value = "some href"
    comm = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="not main product image",
                variants=[SimpleNamespace(href=exp_value)],
            ),
            SimpleNamespace(
                typeName="not main product image",
                variants=[SimpleNamespace(href="not exp_value")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value  # type: ignore


def test_get_image_url_main_image_not_s5():
    exp_value = "some href"
    comm = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href=exp_value, quality="S1")],
            ),
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href="not exp_value", quality="S2")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value  # type: ignore


def test_get_image_url_main_image_s5():
    exp_value = "some href"
    comm = SimpleNamespace(
        media=[
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href="not exp_value", quality="S1")],
            ),
            SimpleNamespace(
                typeName="MAIN_PRODUCT_IMAGE",
                variants=[SimpleNamespace(href=exp_value, quality="S5")],
            ),
        ]
    )
    assert get_image_url(comm) == exp_value  # type: ignore


def test_get_weight_no_package_measurements():
    comm = SimpleNamespace(packageMeasurements=None)
    assert get_weight(comm) == 0.0  # type: ignore


def test_get_weight_no_values():
    comm = SimpleNamespace(packageMeasurements=[])
    assert get_weight(comm) == 0.0  # type: ignore


def test_get_weight_no_weight():
    comm = SimpleNamespace(packageMeasurements=[SimpleNamespace(type="not weight")])
    assert get_weight(comm) == 0.0  # type: ignore


def test_get_weight_success():
    exp_value = 10.0
    comm = SimpleNamespace(
        packageMeasurements=[
            SimpleNamespace(type="not weight", valueMetric="not exp_value"),
            SimpleNamespace(type="WEIGHT", valueMetric=exp_value),
        ]
    )
    assert get_weight(comm) == exp_value  # type: ignore


@pytest.mark.parametrize("input", ([], None))
def test_get_child_items_no_input(input: list[Any] | None):
    assert get_child_items(input) == []


def test_get_child_items_success():
    exp_result = {"11111111": 1, "22222222": 3}
    child_items = [
        SimpleNamespace(itemKey=SimpleNamespace(itemNo=item_code), quantity=qty)
        for item_code, qty in exp_result.items()
    ]

    for child in get_child_items(child_items):  # type: ignore
        assert child.qty == exp_result[child.item_code]
        assert child.weight == 0.0
        assert child.name is None


test_data = (
    {
        "name": "default",
        "response": {
            "data": [
                {
                    "itemKey": {"itemType": "ART", "itemNo": "30379118"},
                    "itemKeyGlobal": {"itemType": "ART", "itemNo": "40346924"},
                    "productNameGlobal": "KALLAX",
                    "isBreathTakingItem": False,
                    "isNew": False,
                    "isAssemblyRequired": True,
                    "numberOfPackages": 1,
                    "localisedCommunications": [
                        {
                            "languageCode": "en",
                            "countryCode": "RU",
                            "productName": "KALLAX",
                            "productType": {"id": "20884", "name": "shelving unit"},
                            "validDesign": {"text": "grey/wood effect"},
                            "measurements": {
                                "referenceMeasurements": [
                                    {
                                        "metric": "77x147 cm",
                                        "imperial": '30 3/8x57 7/8 "',
                                    }
                                ],
                                "detailedMeasurements": [
                                    {
                                        "type": "00047",
                                        "typeName": "Width",
                                        "textMetric": "77 cm",
                                        "textImperial": '30 3/8 "',
                                    },
                                    {
                                        "type": "00044",
                                        "typeName": "Depth",
                                        "textMetric": "39 cm",
                                        "textImperial": '15 3/8 "',
                                    },
                                    {
                                        "type": "00041",
                                        "typeName": "Height",
                                        "textMetric": "147 cm",
                                        "textImperial": '57 7/8 "',
                                    },
                                    {
                                        "type": "00011",
                                        "typeName": "Max. load/shelf",
                                        "textMetric": "13 kg",
                                        "textImperial": "29 lb",
                                    },
                                ],
                            },
                            "designers": [{"id": "10402", "name": "Tord Björklund"}],
                            "media": [
                                {
                                    "id": "0494558",
                                    "peNo": "PE627165",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect MPP",
                                    "altText": "KALLAX Shelving unit, grey/wood effect, 77x147 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494558_pe627165_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494558_pe627165_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494558_pe627165_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494558_pe627165_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494558_pe627165_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "1051326",
                                    "peNo": "PE845149",
                                    "typeNo": "00024",
                                    "typeName": "CONTEXT_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect CPP3",
                                    "altText": "KALLAX Shelving unit, grey/wood effect, 77x147 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__1051326_pe845149_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__1051326_pe845149_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__1051326_pe845149_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__1051326_pe845149_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__1051326_pe845149_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0494559",
                                    "peNo": "PE627164",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect FPP",
                                    "altText": "KALLAX Shelving unit, grey/wood effect, 77x147 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494559_pe627164_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494559_pe627164_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494559_pe627164_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494559_pe627164_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0494559_pe627164_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0545555",
                                    "peNo": "PE655490",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "KALLAX shelving unit 77x147 white MI",
                                    "altText": "KALLAX Shelving unit, grey/wood effect, 77x147 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0545555_pe655490_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0545555_pe655490_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0545555_pe655490_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0545555_pe655490_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/kallax-shelving-unit-grey-wood-effect__0545555_pe655490_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "careInstructions": [
                                {
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Wipe clean with a soft cloth dampened in water and a mild washing-up detergent or soap, if necessary."
                                        },
                                        {
                                            "careInstructionText": "Wipe dry with a clean cloth."
                                        },
                                    ]
                                }
                            ],
                            "benefits": [
                                "You can use the furniture as a room divider because it looks good from every angle.",
                                "Choose whether you want to place it vertically or horizontally and use it as a shelf or sideboard.",
                            ],
                            "longBenefits": [
                                {
                                    "subject": "Material",
                                    "header": "What is constructed board?",
                                    "name": "What is constructed board_general/cross-HFB text",
                                    "text": "We use constructed boards when manufacturing many of our pieces of furniture, such as tables and wardrobes. They are light and resource-efficient, yet still stable and strong. Each board has a frame made of chipboard, fibreboard or solid wood, while the inside is a honeycomb filling structure made of mostly recycled paper, which is extra durable thanks to its special construction. The board is then covered with a protective paint, foil or veneer depending on the style wanted.",
                                }
                            ],
                            "materials": [
                                {
                                    "partMaterials": [
                                        {
                                            "materialText": "Particleboard, Fibreboard, Paper foil, Printed and embossed acrylic paint, Honeycomb structure paper filling (min. 70% recycled), Plastic edging, ABS plastic"
                                        }
                                    ]
                                }
                            ],
                            "environmentTexts": [
                                {
                                    "text": "By using fibreboard with a particle board frame and honeycomb paper as filling material in this product, we use less wood per product. That way, we take better care of resources."
                                },
                                {
                                    "text": "We want to have a positive impact on the planet. That is why by 2030, we want all materials in our products to be recycled or renewable, and sourced in responsible ways."
                                },
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Warning",
                                    "text": "This furniture must be fixed to the wall with the enclosed wall fastener.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Different wall materials require different types of fixing devices. Use fixing devices suitable for the walls in your home, sold separately.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Two persons are needed for the assembly of this furniture.",
                                },
                                {
                                    "type": "Purchase-/Other information",
                                    "text": "This furniture can take a max load of 25 kg on the top.",
                                },
                                {
                                    "type": "May be completed",
                                    "text": "May be completed with KALLAX insert, sold separately.",
                                },
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Height",
                                    "textMetric": "16 cm",
                                    "textImperial": '6 ¼ "',
                                    "valueMetric": "16",
                                    "valueImperial": "6.25",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Length",
                                    "textMetric": "149 cm",
                                    "textImperial": '58 ¾ "',
                                    "valueMetric": "149",
                                    "valueImperial": "58.75",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Net weight",
                                    "textMetric": "20.01 kg",
                                    "textImperial": "44 lb 2 oz",
                                    "valueMetric": "20.01",
                                    "valueImperial": "44.125",
                                    "unitMetric": "kg",
                                    "unitImperial": "pound",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Volume",
                                    "textMetric": "96.6 l",
                                    "textImperial": "3.41 cu.ft",
                                    "valueMetric": "96.6",
                                    "valueImperial": "3.41",
                                    "unitMetric": "litre",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Weight",
                                    "textMetric": "21.28 kg",
                                    "textImperial": "46 lb 15 oz",
                                    "valueMetric": "21.28",
                                    "valueImperial": "46.938",
                                    "unitMetric": "kg",
                                    "unitImperial": "pound",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Width",
                                    "textMetric": "41 cm",
                                    "textImperial": '16 "',
                                    "valueMetric": "41",
                                    "valueImperial": "16",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                            ],
                            "attachments": [
                                {
                                    "type": "ASSEMBLY_INSTRUCTIONS",
                                    "href": "https://www.ikea.com/ru/en/assembly_instructions/kallax-shelving-unit-grey-wood-effect__AA-1055145-9.pdf",
                                }
                            ],
                            "fullLengthTexts": {
                                "subjectId": "000000000000002",
                                "texts": [
                                    {"id": "Name", "value": "Wood"},
                                    {
                                        "id": "Main Headline",
                                        "value": "Our take on wood",
                                    },
                                    {
                                        "id": "Introduction",
                                        "value": "Wood is the material most commonly associated with IKEA furniture, and for good reasons. It’s renewable, recyclable, durable, ages beautifully and it is an important part of our Scandinavian design heritage.  \n \nAt IKEA we believe that sourced in responsible way, wood is a key change driver for climate mitigation. In 2012, we set a goal that by 2020 our wood would be from more sustainable sources. We are happy to announce that we have reached this goal and today, more than 98% of the wood used for IKEA products is either FSC-certified or recycled.",
                                    },
                                    {
                                        "id": "Sub-Heading",
                                        "value": "Forests are critical for life on earth",
                                    },
                                    {
                                        "id": "Body Text",
                                        "value": "Forests contribute to maintaining balance in the atmosphere, purify the air that we breathe and are part of the water cycle. They nourish wildlife biodiversity and provide homes for indigenous communities who depend on forests for their livelihoods. 90% of plant and animal species living on the planet need forests to survive. They provide sources of food, fuel, timber and many other ecosystem services that we rely upon.  \n\nSourcing approximately 19 million m3 of roundwood per year from some 50 countries, IKEA has a significant impact on the world’s forests and the timber industry and a huge responsibility to positively influence how wood is sourced. Responsible wood sourcing and forest management ensure that the needs of people dependent on forests are met, that businesses can work sustainably, that forest ecosystems are protected and biodiversity is enhanced.",
                                    },
                                    {
                                        "id": "Additional Sub-Heading 1",
                                        "value": "100% wood from more sustainable sources",
                                    },
                                    {
                                        "id": "Additional Body Text 1",
                                        "value": "At IKEA, we work with strict industry standards to promote responsible forestry. We don’t allow any wood in our supply chain from forest areas that are illegal or contain high conservation values or from forest areas with social conflict. \n\nBefore starting to work with IKEA, suppliers must demonstrate that they meet IKEA critical requirements on wood sourcing. IKEA requires all suppliers to source wood from more sustainable sources (FSC-certified or recycled wood). All suppliers are audited regularly and non-compliant suppliers are required to implement immediate corrective actions. \n\nBy working together with our suppliers, we are proud to announce that we have reached our more sustainable sources goal, which we set out to achieve by 2020. Today more than 98% of the wood used for IKEA products is either FSC-certified or recycled.",
                                    },
                                    {
                                        "id": "Additional Sub-Heading 2",
                                        "value": "IKEA Forest Positive Agenda for 2030",
                                    },
                                    {
                                        "id": "Additional Body Text 2",
                                        "value": "As pressure on the world’s forests and the surrounding eco-systems increases due to unsustainable agriculture, the expansion of infrastructure and illegal logging, it is time to take an even more holistic approach to protect and support these important resources for generations to come.\n\nThe IKEA Forest Positive Agenda for 2030 set out to improve forest management, enhance biodiversity, mitigate climate change and support the rights and needs of people who depend on forests across the whole supply chain and drive innovation to use wood in even smarter ways. The agenda focuses on three key areas:\n\n•\tMaking responsible forest management the norm across the world.\n•\tHalting deforestation and reforesting degraded landscapes.\n•\tDriving innovation to use wood in smarter ways by designing all products from the very beginning to be reused, refurbished, remanufactured, and eventually recycled.",
                                    },
                                    {
                                        "id": "Additional Sub-Heading 3",
                                        "value": "We accomplish more by working together",
                                    },
                                    {
                                        "id": "Additional Body Text 3",
                                        "value": "For many years, IKEA has partnered with businesses, governments, social groups and non-governmental organisations to fight forest degradation and deforestation and increase the volume and availability of wood from responsibly managed forests both for our own supply chain and beyond. \n\n We are on a journey to improve global forest management and make responsible wood sourcing the industry standard, contributing to building resilient forest landscapes and improve biodiversity.",
                                    },
                                ],
                            },
                            "filterInformation": {
                                "measurementFilters": [
                                    {
                                        "type": "HEIGHT",
                                        "typeName": "Height",
                                        "textMetric": "147 cm",
                                        "textImperial": '57 7/8 "',
                                        "valueMetric": "147",
                                        "valueImperial": "57.874015748031525",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "DEPTH",
                                        "typeName": "Depth",
                                        "textMetric": "39 cm",
                                        "textImperial": '15 3/8 "',
                                        "valueMetric": "39",
                                        "valueImperial": "15.354330708661426",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "WIDTH",
                                        "typeName": "Width",
                                        "textMetric": "77 cm",
                                        "textImperial": '30 3/8 "',
                                        "valueMetric": "77",
                                        "valueImperial": "30.314960629921277",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                ],
                                "classFilters": [
                                    {
                                        "id": "38764",
                                        "name": "Colour",
                                        "values": [{"id": "10028", "name": "grey"}],
                                    },
                                    {
                                        "id": "38765",
                                        "name": "Material",
                                        "values": [
                                            {
                                                "id": "47349",
                                                "name": "Wood (including board)",
                                            }
                                        ],
                                    },
                                    {
                                        "id": "47352",
                                        "name": "Features",
                                        "values": [
                                            {"id": "53039", "name": "With shelves"}
                                        ],
                                    },
                                    {
                                        "id": "47688",
                                        "name": "Doors",
                                        "values": [
                                            {"id": "47687", "name": "Without doors"}
                                        ],
                                    },
                                ],
                            },
                            "benefitSummary": "Standing or lying – KALLAX series is eager to please and will adapt to your taste, space, budget and needs. Fine tune with drawers, shelves, boxes and inserts.",
                            "itemNameLocal": "KALLAX shelving unit 77x147 grey/wood effect RU",
                        },
                        {
                            "languageCode": "ru",
                            "countryCode": "RU",
                            "productName": "KALLAX КАЛЛАКС",
                            "productType": {"id": "20884", "name": "стеллаж"},
                            "validDesign": {"text": "серый/под дерево"},
                            "measurements": {
                                "referenceMeasurements": [
                                    {
                                        "metric": "77x147 см",
                                        "imperial": "30 3/8x57 7/8 дюйм",
                                    }
                                ],
                                "detailedMeasurements": [
                                    {
                                        "type": "00047",
                                        "typeName": "Ширина",
                                        "textMetric": "77 см",
                                        "textImperial": "30 3/8 дюйм",
                                    },
                                    {
                                        "type": "00044",
                                        "typeName": "Глубина",
                                        "textMetric": "39 см",
                                        "textImperial": "15 3/8 дюйм",
                                    },
                                    {
                                        "type": "00041",
                                        "typeName": "Высота",
                                        "textMetric": "147 см",
                                        "textImperial": "57 7/8 дюйм",
                                    },
                                    {
                                        "type": "00011",
                                        "typeName": "Макс нагрузка на полку",
                                        "textMetric": "13 кг",
                                        "textImperial": "29 фнт",
                                    },
                                ],
                            },
                            "designers": [{"id": "10402", "name": "Tord Björklund"}],
                            "media": [
                                {
                                    "id": "0494558",
                                    "peNo": "PE627165",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect MPP",
                                    "altText": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494558_PE627165_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494558_pe627165_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "1051326",
                                    "peNo": "PE845149",
                                    "typeNo": "00024",
                                    "typeName": "CONTEXT_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect CPP3",
                                    "altText": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1051326_PE845149_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__1051326_pe845149_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0494559",
                                    "peNo": "PE627164",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "KALLAX shelving unit 77x147 grey/wood effect FPP",
                                    "altText": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494559_pe627164_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494559_pe627164_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494559_pe627164_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494559_pe627164_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0494559_PE627164_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0494559_pe627164_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0545555",
                                    "peNo": "PE655490",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "KALLAX shelving unit 77x147 white MI",
                                    "altText": "KALLAX КАЛЛАКС Стеллаж, серый/под дерево, 77x147 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0545555_pe655490_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0545555_pe655490_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0545555_pe655490_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0545555_pe655490_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0545555_PE655490_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/kallax-kallaks-stellazh-seryy-pod-derevo__0545555_pe655490_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "careInstructions": [
                                {
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Протирать мягкой влажной тканью, при необходимости можно использовать слабый мыльный раствор."
                                        },
                                        {
                                            "careInstructionText": "Вытирать чистой сухой тканью."
                                        },
                                    ]
                                }
                            ],
                            "benefits": [
                                "Можно использовать для разделения комнаты.",
                                "Можно установить вертикально или горизонтально и использовать как стеллаж или сервант.",
                            ],
                            "materials": [
                                {
                                    "partMaterials": [
                                        {
                                            "materialText": "ДСП, ДВП, Бумажная пленка, Акриловая краска с тиснением и печатным рисунком, Сотовидный бумажный наполнитель (мин. 70 % переработанного материала), Пластиковая окантовка, Пластмасса АБС"
                                        }
                                    ]
                                }
                            ],
                            "environmentTexts": [
                                {
                                    "text": "Используя в этом товаре щит из ДВП и ДСП с сотовидным бумажным наполнителем, мы расходуем меньше древесины, а значит, бережнее относимся к ресурсам планеты."
                                },
                                {
                                    "text": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы."
                                },
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Warning",
                                    "text": "Эту мебель необходимо крепить к стене с помощью прилагаемого стенного крепежа.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Для разных стен требуются различные крепежные приспособления. Подберите подходящие для ваших стен шурупы, дюбели, саморезы и т. п. (не прилагаются).",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Для сборки этой мебели требуются два человека.",
                                },
                                {
                                    "type": "Purchase-/Other information",
                                    "text": "Максимальная нагрузка на верхнюю панель этой мебели: 25 кг.",
                                },
                                {
                                    "type": "May be completed",
                                    "text": "Можно дополнить вставкой КАЛЛАКС, продается отдельно.",
                                },
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Высота",
                                    "textMetric": "16 см",
                                    "textImperial": "6 ¼ дюйм",
                                    "valueMetric": "16",
                                    "valueImperial": "6.25",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Длина",
                                    "textMetric": "149 см",
                                    "textImperial": "58 ¾ дюйм",
                                    "valueMetric": "149",
                                    "valueImperial": "58.75",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Вес нетто",
                                    "textMetric": "20.01 кг",
                                    "textImperial": "44 фнт 2 унц",
                                    "valueMetric": "20.01",
                                    "valueImperial": "44.125",
                                    "unitMetric": "кг",
                                    "unitImperial": "фнт",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Объем",
                                    "textMetric": "96.6 л",
                                    "textImperial": "3.41 cu.ft",
                                    "valueMetric": "96.6",
                                    "valueImperial": "3.41",
                                    "unitMetric": "л",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Вес",
                                    "textMetric": "21.28 кг",
                                    "textImperial": "46 фнт 15 унц",
                                    "valueMetric": "21.28",
                                    "valueImperial": "46.938",
                                    "unitMetric": "кг",
                                    "unitImperial": "фнт",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Ширина",
                                    "textMetric": "41 см",
                                    "textImperial": "16 дюйм",
                                    "valueMetric": "41",
                                    "valueImperial": "16",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                            ],
                            "attachments": [
                                {
                                    "type": "ASSEMBLY_INSTRUCTIONS",
                                    "href": "https://www.ikea.com/ru/ru/assembly_instructions/kallax-kallaks-stellazh-seryy-pod-derevo__AA-1055145-9.pdf",
                                }
                            ],
                            "filterInformation": {
                                "measurementFilters": [
                                    {
                                        "type": "HEIGHT",
                                        "typeName": "Высота",
                                        "textMetric": "147 см",
                                        "textImperial": "57 7/8 дюйм",
                                        "valueMetric": "147",
                                        "valueImperial": "57.874015748031525",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "DEPTH",
                                        "typeName": "Глубина",
                                        "textMetric": "39 см",
                                        "textImperial": "15 3/8 дюйм",
                                        "valueMetric": "39",
                                        "valueImperial": "15.354330708661426",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "WIDTH",
                                        "typeName": "Ширина",
                                        "textMetric": "77 см",
                                        "textImperial": "30 3/8 дюйм",
                                        "valueMetric": "77",
                                        "valueImperial": "30.314960629921277",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                ],
                                "classFilters": [
                                    {
                                        "id": "38764",
                                        "name": "Цвет",
                                        "values": [{"id": "10028", "name": "серый"}],
                                    },
                                    {
                                        "id": "38765",
                                        "name": "Материал",
                                        "values": [
                                            {
                                                "id": "47349",
                                                "name": "Древесина (в т. ч. доска)",
                                            }
                                        ],
                                    },
                                    {
                                        "id": "47352",
                                        "name": "Свойства",
                                        "values": [
                                            {"id": "53039", "name": "С полками"}
                                        ],
                                    },
                                    {
                                        "id": "47688",
                                        "name": "Дверцы",
                                        "values": [
                                            {"id": "47687", "name": "Без дверей"}
                                        ],
                                    },
                                ],
                            },
                            "benefitSummary": "Вертикально или горизонтально — серия КАЛЛАКС всегда адаптируется к вашему вкусу, пространству, бюджету и потребностям. Можно дополнить ящиками, полками, коробками и вставками.",
                            "itemNameLocal": "КАЛЛАКС стел 77x147 серый/под дерево RU",
                        },
                    ],
                    "complementaryItems": [
                        {
                            "itemKey": {"itemType": "ART", "itemNo": "60376420"},
                            "type": "MAY_BE_COMPLETED_WITH",
                        }
                    ],
                    "unitCode": "PIECE",
                    "filterClasses": ["open storage solutions"],
                    "styleGroup": "Basic Modern",
                    "serviceProductRelations": [
                        {
                            "serviceProductId": "ASSEMBLY",
                            "serviceKey": {"itemType": "SGR", "itemNo": "50000960"},
                            "serviceProductType": "ASSEMBLY",
                            "relationType": "SOLD_WITH",
                            "isCoWorkerAssistanceNeeded": False,
                            "isPromoted": False,
                            "recommendationRank": 1,
                        }
                    ],
                    "classUnitKey": {"classUnitType": "RU", "classUnitCode": "RU"},
                    "businessStructure": {
                        "productAreaNo": "0215",
                        "productAreaName": "Open shelving units",
                        "productRangeAreaNo": "021",
                        "productRangeAreaName": "Storage.",
                        "homeFurnishingBusinessNo": "02",
                        "homeFurnishingBusinessName": "Store and organise furniture",
                    },
                    "news": {"value": False},
                    "catalogueReferences": [
                        {"catalogueId": "products", "categoryId": "10382"},
                        {"catalogueId": "products", "categoryId": "10412"},
                        {"catalogueId": "products", "categoryId": "11465"},
                        {"catalogueId": "products", "categoryId": "55012"},
                        {"catalogueId": "series", "categoryId": "27534"},
                    ],
                    "lastChance": {"value": False},
                    "professionalAssemblyTime": {"value": 26, "unit": "MINUTES"},
                    "genericProduct": {"gprNo": "27285"},
                    "productTags": [{"name": "SUITABLE_FOR_BUSINESS"}],
                }
            ]
        },
    },
    {
        "name": "combination",
        "response": {
            "data": [
                {
                    "itemKey": {"itemType": "SPR", "itemNo": "49443609"},
                    "itemKeyGlobal": {"itemType": "SPR", "itemNo": "59429957"},
                    "productNameGlobal": "EKET",
                    "isBreathTakingItem": False,
                    "isNew": True,
                    "isAssemblyRequired": True,
                    "numberOfPackages": 8,
                    "childItems": [
                        {
                            "quantity": 2,
                            "itemKey": {"itemType": "ART", "itemNo": "40510858"},
                            "itemKeyGlobal": {"itemType": "ART", "itemNo": "00510855"},
                        },
                        {
                            "quantity": 2,
                            "itemKey": {"itemType": "ART", "itemNo": "40359389"},
                            "itemKeyGlobal": {"itemType": "ART", "itemNo": "30334605"},
                        },
                        {
                            "quantity": 2,
                            "itemKey": {"itemType": "ART", "itemNo": "30359342"},
                            "itemKeyGlobal": {"itemType": "ART", "itemNo": "80340048"},
                        },
                        {
                            "quantity": 2,
                            "itemKey": {"itemType": "ART", "itemNo": "10359343"},
                            "itemKeyGlobal": {"itemType": "ART", "itemNo": "00340047"},
                        },
                    ],
                    "localisedCommunications": [
                        {
                            "languageCode": "en",
                            "countryCode": "RU",
                            "productName": "EKET",
                            "productType": {
                                "id": "33248",
                                "name": "wall-mounted cabinet combination",
                            },
                            "validDesign": {"text": "white/light green"},
                            "measurements": {
                                "referenceMeasurements": [
                                    {
                                        "metric": "175x25x70 cm",
                                        "imperial": '68 7/8x9 7/8x27 1/2 "',
                                    }
                                ],
                                "detailedMeasurements": [
                                    {
                                        "type": "00001",
                                        "typeName": "Length",
                                        "textMetric": "70 cm",
                                        "textImperial": '27 ½ "',
                                    },
                                    {
                                        "type": "00047",
                                        "typeName": "Width",
                                        "textMetric": "175 cm",
                                        "textImperial": '69 "',
                                    },
                                    {
                                        "type": "00044",
                                        "typeName": "Depth",
                                        "textMetric": "25 cm",
                                        "textImperial": '9 ¾ "',
                                    },
                                    {
                                        "type": "00041",
                                        "typeName": "Height",
                                        "textMetric": "70 cm",
                                        "textImperial": '27 ½ "',
                                    },
                                ],
                            },
                            "media": [
                                {
                                    "id": "1016294",
                                    "peNo": "PE830298",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "EKET wll-mntd cab comb 175x25x70 white/light green MPP",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1016294_pe830298_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1016294_pe830298_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1016294_pe830298_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1016294_pe830298_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1016294_pe830298_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "1038941",
                                    "peNo": "PE840083",
                                    "typeNo": "00017",
                                    "typeName": "INSPIRATIONAL_IMAGE",
                                    "name": "EKET wll-mntd cab comb 175x25x70 white/light green IPP",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1038941_pe840083_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1038941_pe840083_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1038941_pe840083_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1038941_pe840083_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__1038941_pe840083_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0476236",
                                    "peNo": "PE616178",
                                    "typeNo": "00015",
                                    "typeName": "QUALITY_PRODUCT_IMAGE",
                                    "name": "EKET cab w dr/1 shlf 35x35x70 white QPP2",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0476236_pe616178_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0476236_pe616178_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0476236_pe616178_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0476236_pe616178_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0476236_pe616178_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0843151",
                                    "peNo": "PE616267",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "EKET susp rl 35 FPP2",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843151_pe616267_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843151_pe616267_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843151_pe616267_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843151_pe616267_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843151_pe616267_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0843100",
                                    "peNo": "PE619666",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "EKET cabinet w 2 drw 70x35x35 white FPP5",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843100_pe619666_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843100_pe619666_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843100_pe619666_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843100_pe619666_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0843100_pe619666_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0553787",
                                    "peNo": "PE659557",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "EKET cab w 2 drs/2 shlvs 70x25x70 white MI",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0553787_pe659557_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0553787_pe659557_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0553787_pe659557_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0553787_pe659557_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0553787_pe659557_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0631833",
                                    "peNo": "PE695225",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "EKET cabinet 35x25x35 white MI2",
                                    "altText": "EKET Wall-mounted cabinet combination, white/light green, 175x25x70 cm",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0631833_pe695225_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0631833_pe695225_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0631833_pe695225_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0631833_pe695225_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/eket-wall-mounted-cabinet-combination-white-light-green__0631833_pe695225_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "careInstructions": [
                                {
                                    "productTypeText": "Wall-mounted cabinet combination",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Wipe clean with a cloth dampened in a mild cleaner."
                                        }
                                    ],
                                },
                                {
                                    "productTypeText": "Cabinet",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Wipe dry with a clean cloth."
                                        }
                                    ],
                                },
                                {
                                    "productTypeText": "Cabinet w 2 doors and 2 shelves/suspension rail",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Wipe dry with a clean cloth."
                                        },
                                        {
                                            "careInstructionText": "Check regularly that all assembly fastenings are properly tightened and retighten when necessary."
                                        },
                                    ],
                                },
                            ],
                            "benefits": [
                                "With wall-mounted EKET, you make the most of the wall area, while freeing up space on the floor.",
                                "Hide or display your things by combining open and closed storage.",
                                "The door has an integrated push-opener, so you can open it with just a light push.",
                                "4 movable shelves make it easy to adapt the space to your storage needs, while one shelf fixed in place adds increased stability.",
                            ],
                            "materials": [
                                {
                                    "productTypeText": "Cabinet",
                                    "partMaterials": [
                                        {
                                            "partText": "Back panel:",
                                            "materialText": "Fibreboard, Paper foil, Paper foil",
                                        },
                                        {
                                            "partText": "Panel:",
                                            "materialText": "Particleboard, Honeycomb structure paper filling (100% recycled), Fibreboard, Paper foil, Plastic edging",
                                        },
                                    ],
                                },
                                {
                                    "productTypeText": "Cabinet w 2 doors and 2 shelves",
                                    "partMaterials": [
                                        {
                                            "partText": "Panel:",
                                            "materialText": "Particleboard, Honeycomb structure paper filling (100% recycled), Fibreboard, Paper foil, Plastic edging",
                                        },
                                        {
                                            "partText": "Back panel:",
                                            "materialText": "Fibreboard, Paper foil, Plastic foil",
                                        },
                                    ],
                                },
                                {
                                    "productTypeText": "Suspension rail",
                                    "partMaterials": [
                                        {"materialText": "Galvanized steel"}
                                    ],
                                },
                            ],
                            "environmentTexts": [
                                {
                                    "productTypeText": "Cabinet/cabinet w 2 doors and 2 shelves",
                                    "text": "By using fibreboard with a particle board frame and honeycomb paper as filling material in this product, we use less wood per product. That way, we take better care of resources.",
                                },
                                {
                                    "productTypeText": "Cabinet/cabinet w 2 doors and 2 shelves",
                                    "text": "We want to have a positive impact on the planet. That is why by 2030, we want all materials in our products to be recycled or renewable, and sourced in responsible ways.",
                                },
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Included",
                                    "text": "EKET suspension rails for wall mounting are included.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Different wall materials require different types of fixing devices. Use fixing devices suitable for the walls in your home, sold separately.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "The max load for a wall-hung cabinet depends on the wall material.",
                                },
                            ],
                            "filterInformation": {
                                "measurementFilters": [
                                    {
                                        "type": "HEIGHT",
                                        "typeName": "Height",
                                        "textMetric": "70 cm",
                                        "textImperial": '27 ½ "',
                                        "valueMetric": "70",
                                        "valueImperial": "27.55905511811025",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "DEPTH",
                                        "typeName": "Depth",
                                        "textMetric": "25 cm",
                                        "textImperial": '9 ¾ "',
                                        "valueMetric": "25",
                                        "valueImperial": "9.842519685039376",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "WIDTH",
                                        "typeName": "Width",
                                        "textMetric": "175 cm",
                                        "textImperial": '69 "',
                                        "valueMetric": "175",
                                        "valueImperial": "68.89763779527563",
                                        "unitMetric": "cm",
                                        "unitImperial": "inch",
                                    },
                                ]
                            },
                            "benefitSummary": "Dress your wall with EKET! Create a classic storage solution with just a few cabinets or combine as many as you like in a fun and unexpected way to fit your needs and make your space more personal.",
                            "itemNameLocal": "EKET wll-mntd cab comb 175x25x70 white/lgreen RU",
                        },
                        {
                            "languageCode": "ru",
                            "countryCode": "RU",
                            "productName": "EKET ЭКЕТ",
                            "productType": {
                                "id": "33248",
                                "name": "комбинация настенных шкафов",
                            },
                            "validDesign": {"text": "белый/светло-зеленый"},
                            "measurements": {
                                "referenceMeasurements": [
                                    {
                                        "metric": "175x25x70 см",
                                        "imperial": "68 7/8x9 7/8x27 1/2 дюйм",
                                    }
                                ],
                                "detailedMeasurements": [
                                    {
                                        "type": "00001",
                                        "typeName": "Длина",
                                        "textMetric": "70 см",
                                        "textImperial": "27 ½ дюйм",
                                    },
                                    {
                                        "type": "00047",
                                        "typeName": "Ширина",
                                        "textMetric": "175 см",
                                        "textImperial": "69 дюйм",
                                    },
                                    {
                                        "type": "00044",
                                        "typeName": "Глубина",
                                        "textMetric": "25 см",
                                        "textImperial": "9 ¾ дюйм",
                                    },
                                    {
                                        "type": "00041",
                                        "typeName": "Высота",
                                        "textMetric": "70 см",
                                        "textImperial": "27 ½ дюйм",
                                    },
                                ],
                            },
                            "media": [
                                {
                                    "id": "1016294",
                                    "peNo": "PE830298",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "EKET wll-mntd cab comb 175x25x70 white/light green MPP",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1016294_pe830298_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1016294_pe830298_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1016294_pe830298_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1016294_pe830298_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1016294_PE830298_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1016294_pe830298_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "1038941",
                                    "peNo": "PE840083",
                                    "typeNo": "00017",
                                    "typeName": "INSPIRATIONAL_IMAGE",
                                    "name": "EKET wll-mntd cab comb 175x25x70 white/light green IPP",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1038941_pe840083_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1038941_pe840083_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1038941_pe840083_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1038941_pe840083_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "1038941_PE840083_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__1038941_pe840083_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0476236",
                                    "peNo": "PE616178",
                                    "typeNo": "00015",
                                    "typeName": "QUALITY_PRODUCT_IMAGE",
                                    "name": "EKET cab w dr/1 shlf 35x35x70 white QPP2",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0476236_pe616178_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0476236_pe616178_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0476236_pe616178_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0476236_pe616178_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0476236_PE616178_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0476236_pe616178_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0843151",
                                    "peNo": "PE616267",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "EKET susp rl 35 FPP2",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843151_pe616267_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843151_pe616267_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843151_pe616267_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843151_pe616267_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843151_PE616267_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843151_pe616267_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0843100",
                                    "peNo": "PE619666",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "EKET cabinet w 2 drw 70x35x35 white FPP5",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843100_pe619666_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843100_pe619666_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843100_pe619666_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843100_pe619666_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0843100_PE619666_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0843100_pe619666_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0553787",
                                    "peNo": "PE659557",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "EKET cab w 2 drs/2 shlvs 70x25x70 white MI",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0553787_pe659557_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0553787_pe659557_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0553787_pe659557_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0553787_pe659557_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0553787_PE659557_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0553787_pe659557_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0631833",
                                    "peNo": "PE695225",
                                    "typeNo": "00019",
                                    "typeName": "MEASUREMENT_ILLUSTRATION",
                                    "name": "EKET cabinet 35x25x35 white MI2",
                                    "altText": "EKET ЭКЕТ Комбинация настенных шкафов, белый/светло-зеленый, 175x25x70 см",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0631833_pe695225_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0631833_pe695225_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0631833_pe695225_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0631833_pe695225_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0631833_PE695225_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/eket-kombinaciya-nastennyh-shkafov-belyy-svetlo-zelenyy__0631833_pe695225_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "careInstructions": [
                                {
                                    "productTypeText": "Комбинация настенных шкафов",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Протирать тканью, смоченной мягким моющим средством."
                                        }
                                    ],
                                },
                                {
                                    "productTypeText": "Шкаф с 2 дверцами и 2 полками/накладная шина",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Вытирать чистой сухой тканью."
                                        },
                                        {
                                            "careInstructionText": "Регулярно проверяйте все крепления и подтягивайте их при необходимости."
                                        },
                                    ],
                                },
                                {
                                    "productTypeText": "Шкаф",
                                    "careInstructionTexts": [
                                        {
                                            "careInstructionText": "Вытирать чистой сухой тканью."
                                        }
                                    ],
                                },
                            ],
                            "benefits": [
                                "Настенная полка ЭКЕТ позволяет сэкономить пространство на полу и максимально эффективно использовать стену.",
                                "Комбинируйте открытое и закрытое хранение в зависимости от потребностей.",
                                "Дверца со встроенным нажимным механизмом открывается легким нажатием.",
                                "4 съемные полки позволяют адаптировать пространство в соответствии с потребностями хранения, одна несъемная полка обеспечивает устойчивость.",
                            ],
                            "materials": [
                                {
                                    "productTypeText": "Шкаф",
                                    "partMaterials": [
                                        {
                                            "partText": "Задняя панель:",
                                            "materialText": "ДВП, Бумажная пленка, Бумажная пленка",
                                        },
                                        {
                                            "partText": "Панель:",
                                            "materialText": "ДСП, Сотовидный бумажный наполнитель (100 % переработанного материала), ДВП, Бумажная пленка, Пластиковая окантовка",
                                        },
                                    ],
                                },
                                {
                                    "productTypeText": "Шкаф с 2 дверцами и 2 полками",
                                    "partMaterials": [
                                        {
                                            "partText": "Панель:",
                                            "materialText": "ДСП, Сотовидный бумажный наполнитель (100 % переработанного материала), ДВП, Бумажная пленка, Пластиковая окантовка",
                                        },
                                        {
                                            "partText": "Задняя панель:",
                                            "materialText": "ДВП, Бумажная пленка, Полимерная пленка",
                                        },
                                    ],
                                },
                                {
                                    "productTypeText": "Накладная шина",
                                    "partMaterials": [
                                        {"materialText": "Оцинкованная сталь"}
                                    ],
                                },
                            ],
                            "environmentTexts": [
                                {
                                    "productTypeText": "Шкаф/шкаф с 2 дверцами и 2 полками",
                                    "text": "Используя в этом товаре щит из ДВП и ДСП с сотовидным бумажным наполнителем, мы расходуем меньше древесины, а значит, бережнее относимся к ресурсам планеты.",
                                },
                                {
                                    "productTypeText": "Шкаф/шкаф с 2 дверцами и 2 полками",
                                    "text": "Мы хотим оказывать позитивное воздействие на экологию планеты. Вот почему мы планируем к 2030 году использовать для изготовления наших товаров только переработанные, возобновляемые и полученные из ответственных источников материалы.",
                                },
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Included",
                                    "text": "Накладные шины ЭКЕТ для фиксации к стене прилагаются.",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Для разных стен требуются различные крепежные приспособления. Подберите подходящие для ваших стен шурупы, дюбели, саморезы и т. п. (не прилагаются).",
                                },
                                {
                                    "type": "Compl. assembly information",
                                    "text": "Максимальная нагрузка на подвесной шкаф зависит от материала стены.",
                                },
                            ],
                            "filterInformation": {
                                "measurementFilters": [
                                    {
                                        "type": "HEIGHT",
                                        "typeName": "Высота",
                                        "textMetric": "70 см",
                                        "textImperial": "27 ½ дюйм",
                                        "valueMetric": "70",
                                        "valueImperial": "27.55905511811025",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "DEPTH",
                                        "typeName": "Глубина",
                                        "textMetric": "25 см",
                                        "textImperial": "9 ¾ дюйм",
                                        "valueMetric": "25",
                                        "valueImperial": "9.842519685039376",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                    {
                                        "type": "WIDTH",
                                        "typeName": "Ширина",
                                        "textMetric": "175 см",
                                        "textImperial": "69 дюйм",
                                        "valueMetric": "175",
                                        "valueImperial": "68.89763779527563",
                                        "unitMetric": "см",
                                        "unitImperial": "inch",
                                    },
                                ]
                            },
                            "benefitSummary": "ЭКЕТ может стать украшением вашей стены! Создайте классическую систему хранения с помощью нескольких шкафов или комбинируйте шкафы так, как вам нравится для неповторимого интерьера, соответствующего вашим потребностям.",
                            "itemNameLocal": "ЭКЕТ кмб нст шк 175x25x70 белый/светло-зеленый RU",
                        },
                    ],
                    "unitCode": "PIECE",
                    "filterClasses": ["open storage solutions"],
                    "serviceProductRelations": [
                        {
                            "serviceProductId": "ASSEMBLY",
                            "serviceKey": {"itemType": "SGR", "itemNo": "50000960"},
                            "serviceProductType": "ASSEMBLY",
                            "relationType": "SOLD_WITH",
                            "isCoWorkerAssistanceNeeded": False,
                            "isPromoted": False,
                            "recommendationRank": 0,
                        }
                    ],
                    "classUnitKey": {"classUnitType": "RU", "classUnitCode": "RU"},
                    "businessStructure": {
                        "productAreaNo": "0212",
                        "productAreaName": "Solitaire cabinets",
                        "productRangeAreaNo": "021",
                        "productRangeAreaName": "Storage.",
                        "homeFurnishingBusinessNo": "02",
                        "homeFurnishingBusinessName": "Store and organise furniture",
                    },
                    "news": {
                        "value": True,
                        "validFrom": "2021-10-26",
                        "validTo": "2022-02-23",
                    },
                    "catalogueReferences": [
                        {"catalogueId": "products", "categoryId": "55015"}
                    ],
                    "lastChance": {"value": False},
                    "professionalAssemblyTime": {"value": 72, "unit": "MINUTES"},
                    "genericProduct": {"gprNo": "37968"},
                    "productTags": [
                        {
                            "name": "NEW",
                            "validFrom": "2021-10-26",
                            "validTo": "2022-02-23",
                        }
                    ],
                }
            ]
        },
    },
    {
        "name": "no validDesign and no referenceMeasurements",
        "response": {
            "data": [
                {
                    "itemKey": {"itemType": "ART", "itemNo": "10122421"},
                    "itemKeyGlobal": {"itemType": "ART", "itemNo": "10122421"},
                    "productNameGlobal": "MARABOU",
                    "isBreathTakingItem": False,
                    "isNew": False,
                    "isAssemblyRequired": False,
                    "numberOfPackages": 1,
                    "localisedCommunications": [
                        {
                            "languageCode": "en",
                            "countryCode": "RU",
                            "productName": "MARABOU",
                            "productType": {
                                "id": "27279",
                                "name": "milk chocolate bar with daim",
                            },
                            "measurements": {
                                "detailedMeasurements": [
                                    {
                                        "type": "00007",
                                        "typeName": "Weight",
                                        "textMetric": "250 g",
                                        "textImperial": "8.8 oz",
                                    }
                                ]
                            },
                            "displayUnit": {
                                "type": "WEIGHT",
                                "unitInformation": {
                                    "unitMetric": "kg",
                                    "unitImperial": "lb",
                                    "unitMetricValue": "0.25",
                                    "unitImperialValue": "0.551",
                                },
                            },
                            "media": [
                                {
                                    "id": "0520599",
                                    "peNo": "PE642300",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "MARABOU milk choc bar w daim 250g MPP",
                                    "altText": "MARABOU Milk chocolate bar with daim",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/marabou-milk-chocolate-bar-with-daim__0520599_pe642300_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/marabou-milk-chocolate-bar-with-daim__0520599_pe642300_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/marabou-milk-chocolate-bar-with-daim__0520599_pe642300_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/marabou-milk-chocolate-bar-with-daim__0520599_pe642300_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/marabou-milk-chocolate-bar-with-daim__0520599_pe642300_s5.jpg",
                                        },
                                    ],
                                }
                            ],
                            "benefits": [
                                "Milk chocolate with crushed pieces of almond caramel."
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Height",
                                    "textMetric": "1 cm",
                                    "textImperial": '½ "',
                                    "valueMetric": "1",
                                    "valueImperial": "½",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Length",
                                    "textMetric": "22 cm",
                                    "textImperial": '8 ¾ "',
                                    "valueMetric": "22",
                                    "valueImperial": "8.75",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Net weight",
                                    "textMetric": "0.25 kg",
                                    "textImperial": "9 oz",
                                    "valueMetric": "0.25",
                                    "valueImperial": "9",
                                    "unitMetric": "kg",
                                    "unitImperial": "ounce",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Volume",
                                    "textMetric": "0.3 l",
                                    "textImperial": "0.01 cu.ft",
                                    "valueMetric": "0.3",
                                    "valueImperial": "0.01",
                                    "unitMetric": "litre",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Weight",
                                    "textMetric": "0.25 kg",
                                    "textImperial": "9 oz",
                                    "valueMetric": "0.25",
                                    "valueImperial": "9",
                                    "unitMetric": "kg",
                                    "unitImperial": "ounce",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Width",
                                    "textMetric": "10 cm",
                                    "textImperial": '4 "',
                                    "valueMetric": "10",
                                    "valueImperial": "4",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                            ],
                            "itemNameLocal": "MARABOU milk choc bar w daim 250g",
                        },
                        {
                            "languageCode": "ru",
                            "countryCode": "RU",
                            "productName": "MARABOU",
                            "productType": {"id": "27279", "name": "шоколад Дайм"},
                            "measurements": {
                                "detailedMeasurements": [
                                    {
                                        "type": "00007",
                                        "typeName": "Вес",
                                        "textMetric": "250 г",
                                        "textImperial": "8.8 унц",
                                    }
                                ]
                            },
                            "displayUnit": {
                                "type": "WEIGHT",
                                "unitInformation": {
                                    "unitMetric": "кг",
                                    "unitImperial": "фнт",
                                    "unitMetricValue": "0.25",
                                    "unitImperialValue": "0.551",
                                },
                            },
                            "media": [
                                {
                                    "id": "0520599",
                                    "peNo": "PE642300",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "MARABOU milk choc bar w daim 250g MPP",
                                    "altText": "MARABOU Шоколад Дайм",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/marabou-shokolad-daym__0520599_pe642300_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/marabou-shokolad-daym__0520599_pe642300_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/marabou-shokolad-daym__0520599_pe642300_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/marabou-shokolad-daym__0520599_pe642300_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0520599_PE642300_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/marabou-shokolad-daym__0520599_pe642300_s5.jpg",
                                        },
                                    ],
                                }
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Высота",
                                    "textMetric": "1 см",
                                    "textImperial": "½ дюйм",
                                    "valueMetric": "1",
                                    "valueImperial": "½",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Длина",
                                    "textMetric": "22 см",
                                    "textImperial": "8 ¾ дюйм",
                                    "valueMetric": "22",
                                    "valueImperial": "8.75",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Вес нетто",
                                    "textMetric": "0.25 кг",
                                    "textImperial": "9 унц",
                                    "valueMetric": "0.25",
                                    "valueImperial": "9",
                                    "unitMetric": "кг",
                                    "unitImperial": "унц",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Объем",
                                    "textMetric": "0.3 л",
                                    "textImperial": "0.01 cu.ft",
                                    "valueMetric": "0.3",
                                    "valueImperial": "0.01",
                                    "unitMetric": "л",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Вес",
                                    "textMetric": "0.25 кг",
                                    "textImperial": "9 унц",
                                    "valueMetric": "0.25",
                                    "valueImperial": "9",
                                    "unitMetric": "кг",
                                    "unitImperial": "унц",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Ширина",
                                    "textMetric": "10 см",
                                    "textImperial": "4 дюйм",
                                    "valueMetric": "10",
                                    "valueImperial": "4",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                            ],
                            "itemNameLocal": "MARABOU шоколад Дайм",
                        },
                    ],
                    "unitCode": "PIECE",
                    "styleGroup": "Multi",
                    "classUnitKey": {"classUnitType": "RU", "classUnitCode": "RU"},
                    "businessStructure": {
                        "productAreaNo": "9616",
                        "productAreaName": "Sweets, chocolate & snacks",
                        "productRangeAreaNo": "961",
                        "productRangeAreaName": "Swedish Food Market",
                        "homeFurnishingBusinessNo": "96",
                        "homeFurnishingBusinessName": "IKEA Food",
                    },
                    "news": {"value": False},
                    "catalogueReferences": [
                        {"catalogueId": "products", "categoryId": "46192"}
                    ],
                    "lastChance": {"value": False},
                }
            ]
        },
    },
    {
        "name": "no measurements",
        "response": {
            "data": [
                {
                    "itemKey": {"itemType": "ART", "itemNo": "30377949"},
                    "itemKeyGlobal": {"itemType": "ART", "itemNo": "80377937"},
                    "productNameGlobal": "FENOMEN",
                    "isBreathTakingItem": False,
                    "isNew": False,
                    "isAssemblyRequired": False,
                    "numberOfPackages": 1,
                    "localisedCommunications": [
                        {
                            "languageCode": "en",
                            "countryCode": "RU",
                            "productName": "FENOMEN",
                            "productType": {
                                "id": "30436",
                                "name": "unscented block candle, set of 5",
                            },
                            "validDesign": {"text": "natural"},
                            "media": [
                                {
                                    "id": "0577466",
                                    "peNo": "PE668898",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 natural MPP",
                                    "altText": "FENOMEN Unscented block candle, set of 5, natural",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0577466_pe668898_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0577466_pe668898_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0577466_pe668898_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0577466_pe668898_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0577466_pe668898_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0904278",
                                    "peNo": "PE670010",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 na FPP",
                                    "altText": "FENOMEN Unscented block candle, set of 5, natural",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0904278_pe670010_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0904278_pe670010_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0904278_pe670010_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0904278_pe670010_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0904278_pe670010_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0669197",
                                    "peNo": "PE714892",
                                    "typeNo": "00017",
                                    "typeName": "INSPIRATIONAL_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 natural IPP",
                                    "altText": "FENOMEN Unscented block candle, set of 5, natural",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S1.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0669197_pe714892_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S2.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0669197_pe714892_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S3.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0669197_pe714892_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S4.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0669197_pe714892_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S5.JPG",
                                            "href": "https://www.ikea.com/ru/en/images/products/fenomen-unscented-block-candle-set-of-5-natural__0669197_pe714892_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "benefits": [
                                "Block candles provide an atmospheric light and are also beautiful home furnishing accessories when not lit.",
                                "Block candles have a long burning time and are beautiful together on a candle dish.",
                            ],
                            "materials": [
                                {
                                    "partMaterials": [
                                        {
                                            "materialText": "paraffin wax, plant based wax"
                                        }
                                    ]
                                }
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Complementary info measurements",
                                    "text": "Size: (height x diameter) 9 cmx5.9 cm (burning time 20h), 12 cmx5.9 cm (burning time 34h), 15 cmx5.9 cm (burning time 40h), 8 cmx6.7 cm (burning time 20h), 13 cmx6.7 cm (burning time 40h).",
                                },
                                {
                                    "type": "Warning",
                                    "text": "Never leave a burning candle unattended.",
                                },
                                {
                                    "type": "Warning",
                                    "text": "Do not burn candles near any flammable materials.",
                                },
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Height",
                                    "textMetric": "7 cm",
                                    "textImperial": '2 ¾ "',
                                    "valueMetric": "7",
                                    "valueImperial": "2.75",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Length",
                                    "textMetric": "22 cm",
                                    "textImperial": '8 ¾ "',
                                    "valueMetric": "22",
                                    "valueImperial": "8.75",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Net weight",
                                    "textMetric": "1.34 kg",
                                    "textImperial": "2 lb 15 oz",
                                    "valueMetric": "1.34",
                                    "valueImperial": "2.938",
                                    "unitMetric": "kg",
                                    "unitImperial": "pound",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Volume",
                                    "textMetric": "2.9 l",
                                    "textImperial": "0.10 cu.ft",
                                    "valueMetric": "2.9",
                                    "valueImperial": "0.10",
                                    "unitMetric": "litre",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Weight",
                                    "textMetric": "1.39 kg",
                                    "textImperial": "3 lb 1 oz",
                                    "valueMetric": "1.39",
                                    "valueImperial": "3.062",
                                    "unitMetric": "kg",
                                    "unitImperial": "pound",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Width",
                                    "textMetric": "19 cm",
                                    "textImperial": '7 ½ "',
                                    "valueMetric": "19",
                                    "valueImperial": "7.5",
                                    "unitMetric": "cm",
                                    "unitImperial": "inch",
                                    "packNo": 1,
                                },
                            ],
                            "filterInformation": {
                                "classFilters": [
                                    {
                                        "id": "38764",
                                        "name": "Colour",
                                        "values": [{"id": "10003", "name": "beige"}],
                                    }
                                ]
                            },
                            "benefitSummary": "The glow from candles can add atmosphere to any moment – they can light up dark mornings, make a one-on-one dinner more romantic or make a room feel warmer and more inviting.",
                            "itemNameLocal": "FENOMEN N unscented blck cndl s5 natural RU",
                        },
                        {
                            "languageCode": "ru",
                            "countryCode": "RU",
                            "productName": "FENOMEN ФЕНОМЕН",
                            "productType": {
                                "id": "30436",
                                "name": "неароматическая формовая свеча, 5шт",
                            },
                            "validDesign": {"text": "естественный"},
                            "media": [
                                {
                                    "id": "0577466",
                                    "peNo": "PE668898",
                                    "typeNo": "00001",
                                    "typeName": "MAIN_PRODUCT_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 natural MPP",
                                    "altText": "FENOMEN ФЕНОМЕН Неароматическая формовая свеча, 5шт, естественный",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0577466_pe668898_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0577466_pe668898_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0577466_pe668898_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0577466_pe668898_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0577466_PE668898_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0577466_pe668898_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0904278",
                                    "peNo": "PE670010",
                                    "typeNo": "00016",
                                    "typeName": "FUNCTIONAL_PRODUCT_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 na FPP",
                                    "altText": "FENOMEN ФЕНОМЕН Неароматическая формовая свеча, 5шт, естественный",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0904278_pe670010_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0904278_pe670010_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0904278_pe670010_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0904278_pe670010_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0904278_PE670010_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0904278_pe670010_s5.jpg",
                                        },
                                    ],
                                },
                                {
                                    "id": "0669197",
                                    "peNo": "PE714892",
                                    "typeNo": "00017",
                                    "typeName": "INSPIRATIONAL_IMAGE",
                                    "name": "FENOMEN N unscented blck cndl s5 natural IPP",
                                    "altText": "FENOMEN ФЕНОМЕН Неароматическая формовая свеча, 5шт, естественный",
                                    "variants": [
                                        {
                                            "quality": "S1",
                                            "height": 40,
                                            "width": 40,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S1.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0669197_pe714892_s1.jpg",
                                        },
                                        {
                                            "quality": "S2",
                                            "height": 110,
                                            "width": 110,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S2.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0669197_pe714892_s2.jpg",
                                        },
                                        {
                                            "quality": "S3",
                                            "height": 250,
                                            "width": 250,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S3.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0669197_pe714892_s3.jpg",
                                        },
                                        {
                                            "quality": "S4",
                                            "height": 500,
                                            "width": 500,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S4.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0669197_pe714892_s4.jpg",
                                        },
                                        {
                                            "quality": "S5",
                                            "height": 2000,
                                            "width": 2000,
                                            "fileMimeType": "image/jpeg",
                                            "fileName": "0669197_PE714892_S5.JPG",
                                            "href": "https://www.ikea.com/ru/ru/images/products/fenomen-nearomaticheskaya-formovaya-svecha-5sht-estestvennyy__0669197_pe714892_s5.jpg",
                                        },
                                    ],
                                },
                            ],
                            "materials": [
                                {
                                    "partMaterials": [
                                        {
                                            "materialText": "парафиновый воск, растительный воск"
                                        }
                                    ]
                                }
                            ],
                            "goodToKnows": [
                                {
                                    "type": "Complementary info measurements",
                                    "text": "Размеры (высота x диаметр): 9 см x 5,9 см (время горения 20 ч.), 12 см x 5,9 см (время горения 34 ч.), 15 см x 5,9 см (время горения 40ч.), 8 см x 6,7 см (время горения 20 ч.), 13 см x 6,7 см (время горения 40 ч.).",
                                },
                                {
                                    "type": "Warning",
                                    "text": "Никогда не оставляйте горящую свечу вне поля зрения.",
                                },
                                {
                                    "type": "Warning",
                                    "text": "Не зажигайте свечи рядом с воспламеняемыми материалами.",
                                },
                            ],
                            "packageMeasurements": [
                                {
                                    "type": "HEIGHT",
                                    "typeName": "Высота",
                                    "textMetric": "7 см",
                                    "textImperial": "2 ¾ дюйм",
                                    "valueMetric": "7",
                                    "valueImperial": "2.75",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "LENGTH",
                                    "typeName": "Длина",
                                    "textMetric": "22 см",
                                    "textImperial": "8 ¾ дюйм",
                                    "valueMetric": "22",
                                    "valueImperial": "8.75",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                                {
                                    "type": "NETWEIGHT",
                                    "typeName": "Вес нетто",
                                    "textMetric": "1.34 кг",
                                    "textImperial": "2 фнт 15 унц",
                                    "valueMetric": "1.34",
                                    "valueImperial": "2.938",
                                    "unitMetric": "кг",
                                    "unitImperial": "фнт",
                                    "packNo": 1,
                                },
                                {
                                    "type": "VOLUME",
                                    "typeName": "Объем",
                                    "textMetric": "2.9 л",
                                    "textImperial": "0.10 cu.ft",
                                    "valueMetric": "2.9",
                                    "valueImperial": "0.10",
                                    "unitMetric": "л",
                                    "unitImperial": "cu.ft",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WEIGHT",
                                    "typeName": "Вес",
                                    "textMetric": "1.39 кг",
                                    "textImperial": "3 фнт 1 унц",
                                    "valueMetric": "1.39",
                                    "valueImperial": "3.062",
                                    "unitMetric": "кг",
                                    "unitImperial": "фнт",
                                    "packNo": 1,
                                },
                                {
                                    "type": "WIDTH",
                                    "typeName": "Ширина",
                                    "textMetric": "19 см",
                                    "textImperial": "7 ½ дюйм",
                                    "valueMetric": "19",
                                    "valueImperial": "7.5",
                                    "unitMetric": "см",
                                    "unitImperial": "дюйм",
                                    "packNo": 1,
                                },
                            ],
                            "filterInformation": {
                                "classFilters": [
                                    {
                                        "id": "38764",
                                        "name": "Цвет",
                                        "values": [{"id": "10003", "name": "бежевый"}],
                                    }
                                ]
                            },
                            "benefitSummary": "Мерцание свечи создаст располагающую атмосферу в любой момент — осветит темное зимнее утро, превратит обычный ужин в романтический и сделает комнату более уютной.",
                            "itemNameLocal": "ФЕНОМЕН N неар фрм свеч, 5шт естественный RU",
                        },
                    ],
                    "complementaryItems": [
                        {
                            "itemKey": {"itemType": "ART", "itemNo": "40380588"},
                            "type": "GETS_SAFER_WITH",
                        },
                        {
                            "itemKey": {"itemType": "ART", "itemNo": "40350039"},
                            "type": "MAY_BE_COMPLETED_WITH",
                        },
                        {
                            "itemKey": {"itemType": "ART", "itemNo": "30388721"},
                            "type": "MAY_BE_COMPLETED_WITH",
                        },
                    ],
                    "unitCode": "PIECE",
                    "filterClasses": ["base"],
                    "styleGroup": "Multi",
                    "classUnitKey": {"classUnitType": "RU", "classUnitCode": "RU"},
                    "businessStructure": {
                        "productAreaNo": "1632",
                        "productAreaName": "Candles and atmosphere light",
                        "productRangeAreaNo": "163",
                        "productRangeAreaName": "Home decoration",
                        "homeFurnishingBusinessNo": "16",
                        "homeFurnishingBusinessName": "Decoration",
                    },
                    "news": {"value": False},
                    "catalogueReferences": [
                        {"catalogueId": "products", "categoryId": "10782"}
                    ],
                    "lastChance": {"value": False},
                }
            ]
        },
    },
)


@pytest.mark.parametrize("test_data_response", test_data)
def test_main(test_data_response: dict[str, Any]):
    list(main(test_data_response["response"]))
