from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from ikea_api.wrappers import types
from ikea_api.wrappers._parsers import translate_from_dict
from ikea_api.wrappers._parsers.order_capture import (
    DELIVERY_TYPES,
    SERVICE_TYPES,
    get_date,
    get_price,
    get_service_provider,
    get_type,
    get_unavailable_items,
    main,
)


def test_get_date_no_value():
    assert get_date([]) is None
    assert get_date([SimpleNamespace(timeWindows=None)]) is None  # type: ignore
    assert (
        get_date(  # type: ignore
            [  # type: ignore
                SimpleNamespace(timeWindows=None),
                SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
            ]
        )
    ) is None


def test_get_date_with_value_first():
    exp_datetime = datetime.now()
    deliveries = [
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(fromDateTime=exp_datetime)
            )
        ),
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(
                    fromDateTime=exp_datetime + timedelta(days=1)
                )
            )
        ),
    ]
    assert get_date(deliveries) == exp_datetime  # type: ignore


def test_get_date_with_value_not_first():
    exp_datetime = datetime.now()
    deliveries = [
        SimpleNamespace(timeWindows=SimpleNamespace(earliestPossibleSlot=None)),
        SimpleNamespace(
            timeWindows=SimpleNamespace(
                earliestPossibleSlot=SimpleNamespace(fromDateTime=exp_datetime)
            )
        ),
    ]
    assert get_date(deliveries) == exp_datetime  # type: ignore


def test_get_type_no_service_type():
    exp_delivery_type = "HOME_DELIVERY"
    service = SimpleNamespace(fulfillmentMethodType=exp_delivery_type, solution=None)
    assert get_type(service) == translate_from_dict(DELIVERY_TYPES, exp_delivery_type)  # type: ignore


def test_get_type_with_service_type():
    exp_delivery_type = "HOME_DELIVERY"
    exp_solution_type = "CURBSIDE"
    service = SimpleNamespace(
        fulfillmentMethodType=exp_delivery_type, solution=exp_solution_type
    )
    assert get_type(service) == (  # type: ignore
        translate_from_dict(DELIVERY_TYPES, exp_delivery_type)
        + f" {translate_from_dict(SERVICE_TYPES, exp_solution_type)}"
    )


def test_get_price_no_value():
    service = SimpleNamespace(solutionPrice=None)
    assert get_price(service) == 0  # type: ignore


def test_get_price_with_value():
    service = SimpleNamespace(solutionPrice=SimpleNamespace(inclTax=100))
    assert get_price(service) == 100  # type: ignore


@pytest.mark.parametrize("v", (None, []))
def test_get_unavailable_items_no_value(v: list[Any] | None):
    assert get_unavailable_items(SimpleNamespace(unavailableItems=v)) == []  # type: ignore


def test_get_unavailable_items_with_value():
    items = [
        SimpleNamespace(itemNo="11111111", availableQuantity=5),
        SimpleNamespace(itemNo="22222222", availableQuantity=3),
    ]
    exp_res = [
        types.UnavailableItem(item_code="11111111", available_qty=5),
        types.UnavailableItem(item_code="22222222", available_qty=3),
    ]
    assert get_unavailable_items(SimpleNamespace(unavailableItems=items)) == exp_res  # type: ignore


def test_get_service_provider_no_value():
    assert get_service_provider(SimpleNamespace(identifier=None)) is None  # type: ignore


@pytest.mark.parametrize("v", ("BUSINESSLINES and some other value", "BUSINESSLINES"))
def test_get_service_provider_with_value_match(v: str):
    service = SimpleNamespace(identifier=v)
    assert get_service_provider(service) == "Деловые линии"  # type: ignore


def test_get_service_provider_with_value_no_match():
    exp_identifier = "USINESSLIN"
    service = SimpleNamespace(identifier=exp_identifier)
    assert get_service_provider(service) == exp_identifier  # type: ignore


test_home_delivery_services_data: list[dict[str, Any]] = [
    {
        "context": {
            "retailUnit": "ru",
            "exclTaxCountry": False,
            "checkoutId": "",
            "currency": "RUB",
            "scope": {"type": "HOME_DELIVERY"},
            "config": {
                "enableLeadTimeOrchestration": True,
                "enablePrimeTimeCalculation": True,
                "allowedPTSDeliveries": [
                    "HOME_DELIVERY_STANDARD",
                    "HOME_DELIVERY_CURBSIDE",
                    "HOME_DELIVERY_EXPRESS",
                    "HOME_DELIVERY_EXPRESS_CURBSIDE",
                ],
            },
            "businessUnit": {"code": "111", "type": "STO"},
            "customerContext": {"customerType": "PRIVATE"},
            "capability": {
                "wheelChair": False,
                "rangeOfDays": True,
                "authToLeave": True,
            },
        },
        "possibleDeliveryServices": {
            "metadata": {"canAtLeastOneSolutionFulfillEntireCart": False},
            "deliveryServices": [
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["UNAVAILABLE_ITEMS"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": True,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "HOME_DELIVERY",
                    "fulfillmentPossibility": "PARTIAL",
                    "solutionId": "HD~1~STANDARD",
                    "solution": "STANDARD",
                    "solutionPrice": {"inclTax": 4399, "exclTax": 3665.83},
                    "expiryTime": "2021-12-27T17:12:49.319Z",
                    "possibleDeliveries": {
                        "metadata": {"multipleDeliveries": False},
                        "deliveries": [
                            {
                                "id": "",
                                "metadata": {"rangeOfDays": False},
                                "fulfillmentDeliveryId": "HD~~~2",
                                "serviceItemId": "SGR40000606",
                                "type": "TRUCK",
                                "deliveryPrice": {"inclTax": 4399, "exclTax": 3665.83},
                                "deliveryItems": [
                                    {
                                        "itemNo": "90503662",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "30308282",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60384364",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "20379538",
                                        "itemType": "ART",
                                        "quantity": 4,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "20299339",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "90488317",
                                        "itemType": "ART",
                                        "quantity": 2,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "80383957",
                                        "itemType": "ART",
                                        "quantity": 2,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60363012",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "30497635",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "90384013",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "50383874",
                                        "itemType": "ART",
                                        "quantity": 3,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "70366642",
                                        "itemType": "ART",
                                        "quantity": 7,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                ],
                                "timeWindows": {
                                    "metadata": {"available": True},
                                    "earliestPossibleSlot": {
                                        "metadata": {
                                            "timeZone": "Europe/Moscow",
                                            "hasPriceDeviation": False,
                                        },
                                        "id": "",
                                        "fromDateTime": "2022-01-19T16:00:00.000",
                                        "toDateTime": "2022-01-19T20:00:00.000",
                                    },
                                },
                            }
                        ],
                    },
                    "unavailableItems": [
                        {
                            "id": "18",
                            "lineId": "18",
                            "itemNo": "80357835",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "17",
                            "lineId": "17",
                            "itemNo": "70480567",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "10",
                            "lineId": "10",
                            "itemNo": "40363013",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "6",
                            "lineId": "6",
                            "itemNo": "20394949",
                            "type": "ART",
                            "requiredQuantity": 4,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "4"
                            },
                        },
                        {
                            "id": "3",
                            "lineId": "3",
                            "itemNo": "10359791",
                            "type": "ART",
                            "requiredQuantity": 4,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "4"
                            },
                        },
                        {
                            "id": "13",
                            "lineId": "13",
                            "itemNo": "60366572",
                            "type": "ART",
                            "requiredQuantity": 2,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "2"
                            },
                        },
                        {
                            "id": "2",
                            "lineId": "2",
                            "itemNo": "00463024",
                            "type": "ART",
                            "requiredQuantity": 2,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "2"
                            },
                        },
                        {
                            "id": "20",
                            "lineId": "20",
                            "itemNo": "90299473",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "16",
                            "lineId": "16",
                            "itemNo": "70366642",
                            "type": "ART",
                            "requiredQuantity": 7,
                            "availableQuantity": 2,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "5"
                            },
                        },
                    ],
                },
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["UNAVAILABLE_ITEMS"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": True,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "HOME_DELIVERY",
                    "fulfillmentPossibility": "PARTIAL",
                    "solutionId": "HD~1~CURBSIDE",
                    "solution": "CURBSIDE",
                    "solutionPrice": {"inclTax": 3799, "exclTax": 3165.83},
                    "expiryTime": "2021-12-27T17:12:49.319Z",
                    "possibleDeliveries": {
                        "metadata": {"multipleDeliveries": False},
                        "deliveries": [
                            {
                                "id": "",
                                "metadata": {"rangeOfDays": False},
                                "fulfillmentDeliveryId": "HD~~~4",
                                "serviceItemId": "SGR90000897",
                                "type": "TRUCK",
                                "deliveryPrice": {"inclTax": 3799, "exclTax": 3165.83},
                                "deliveryItems": [
                                    {
                                        "itemNo": "90503662",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60476349",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "30486397",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "00383881",
                                        "itemType": "ART",
                                        "quantity": 2,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "30308282",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60384364",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "20379538",
                                        "itemType": "ART",
                                        "quantity": 4,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "20299339",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "90488317",
                                        "itemType": "ART",
                                        "quantity": 2,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "80383957",
                                        "itemType": "ART",
                                        "quantity": 2,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60363012",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "30497635",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "90384013",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "50383874",
                                        "itemType": "ART",
                                        "quantity": 3,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "70366642",
                                        "itemType": "ART",
                                        "quantity": 7,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                ],
                                "timeWindows": {
                                    "metadata": {"available": True},
                                    "earliestPossibleSlot": {
                                        "metadata": {
                                            "timeZone": "Europe/Moscow",
                                            "hasPriceDeviation": False,
                                        },
                                        "id": "",
                                        "fromDateTime": "2022-01-19T16:00:00.000",
                                        "toDateTime": "2022-01-19T20:00:00.000",
                                    },
                                },
                            }
                        ],
                    },
                    "unavailableItems": [
                        {
                            "id": "",
                            "lineId": "18",
                            "itemNo": "80357835",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "",
                            "lineId": "17",
                            "itemNo": "70480567",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "",
                            "lineId": "10",
                            "itemNo": "40363013",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "16",
                            "lineId": "16",
                            "itemNo": "70366642",
                            "type": "ART",
                            "requiredQuantity": 7,
                            "availableQuantity": 2,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "5"
                            },
                        },
                    ],
                },
            ],
        },
    },
    {
        "context": {
            "retailUnit": "ru",
            "exclTaxCountry": False,
            "checkoutId": "",
            "currency": "RUB",
            "scope": {"type": "HOME_DELIVERY"},
            "config": {
                "enableLeadTimeOrchestration": True,
                "enablePrimeTimeCalculation": True,
                "allowedPTSDeliveries": [
                    "HOME_DELIVERY_STANDARD",
                    "HOME_DELIVERY_CURBSIDE",
                    "HOME_DELIVERY_EXPRESS",
                    "HOME_DELIVERY_EXPRESS_CURBSIDE",
                ],
            },
            "businessUnit": {"code": "111", "type": "STO"},
            "customerContext": {"customerType": "PRIVATE"},
            "capability": {
                "wheelChair": False,
                "rangeOfDays": True,
                "authToLeave": True,
            },
        },
        "possibleDeliveryServices": {
            "metadata": {"canAtLeastOneSolutionFulfillEntireCart": False},
            "deliveryServices": [
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["DELIVERY_TIME_WINDOW_UNAVAILABLE"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": True,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "HOME_DELIVERY",
                    "fulfillmentPossibility": "FULL",
                    "solutionId": "HD~1~STANDARD",
                    "solution": "STANDARD",
                    "solutionPrice": {"inclTax": 999, "exclTax": 832.5},
                    "expiryTime": "2021-12-27T15:49:41.118Z",
                    "possibleDeliveries": {
                        "metadata": {"multipleDeliveries": False},
                        "deliveries": [
                            {
                                "id": "",
                                "metadata": {"rangeOfDays": False},
                                "fulfillmentDeliveryId": "HD~~~2",
                                "serviceItemId": "SGR50000597",
                                "type": "PARCEL",
                                "deliveryPrice": {"inclTax": 999, "exclTax": 832.5},
                                "deliveryItems": [
                                    {
                                        "itemNo": "30480178",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "10442682",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                ],
                                "timeWindows": {
                                    "metadata": {"available": False},
                                    "error": {
                                        "type": "INTEGRATION_APP_ERROR",
                                        "service": "EARLIEST_POSSIBLE_DELIVERY_TIME_WINDOWS",
                                        "solutionId": "HD~1~STANDARD",
                                        "errorDetail": {
                                            "errorCode": "EXTN_SOMOP_0018",
                                            "errorDescription": "No Lastmile capacity available from Centiro",
                                            "errorUniqueExceptionId": "",
                                        },
                                    },
                                },
                            }
                        ],
                    },
                    "errors": [
                        {
                            "type": "INTEGRATION_APP_ERROR",
                            "service": "EARLIEST_POSSIBLE_DELIVERY_TIME_WINDOWS",
                            "solutionId": "HD~1~STANDARD",
                            "errorDetail": {
                                "errorCode": "EXTN_SOMOP_0018",
                                "errorDescription": "No Lastmile capacity available from Centiro",
                                "errorUniqueExceptionId": "",
                            },
                        }
                    ],
                }
            ],
        },
    },
]
test_collect_delivery_services_data: list[dict[str, Any]] = [
    {
        "context": {
            "retailUnit": "ru",
            "exclTaxCountry": False,
            "checkoutId": "",
            "currency": "RUB",
            "scope": {
                "type": "COLLECT",
                "subTypes": [
                    {"id": "PUP", "maxCollectionPoints": "40"},
                    {"id": "PUOP", "maxCollectionPoints": "20"},
                    {"id": "CLICK_COLLECT_STORE", "maxCollectionPoints": "10"},
                ],
            },
            "config": {
                "enableLeadTimeOrchestration": True,
                "enablePrimeTimeCalculation": True,
                "allowedPTSDeliveries": [
                    "HOME_DELIVERY_STANDARD",
                    "HOME_DELIVERY_CURBSIDE",
                    "HOME_DELIVERY_EXPRESS",
                    "HOME_DELIVERY_EXPRESS_CURBSIDE",
                ],
            },
            "businessUnit": {"code": "111", "type": "STO"},
            "customerContext": {"customerType": "PRIVATE"},
            "capability": {
                "wheelChair": False,
                "rangeOfDays": True,
                "authToLeave": True,
            },
        },
        "possibleDeliveryServices": {
            "metadata": {"canAtLeastOneSolutionFulfillEntireCart": False},
            "deliveryServices": [
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["UNAVAILABLE_ITEMS"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "PUP",
                    "fulfillmentPossibility": "PARTIAL",
                    "solutionId": "PUP~1~1~STANDARD",
                    "solution": "STANDARD",
                    "solutionPrice": {"inclTax": 1399, "exclTax": 1165.83},
                    "expiryTime": "2021-12-27T17:20:04.751Z",
                    "possibleDeliveries": {
                        "metadata": {"multipleDeliveries": False},
                        "deliveries": [
                            {
                                "id": "",
                                "metadata": {"rangeOfDays": False},
                                "fulfillmentDeliveryId": "PUP~~~4",
                                "serviceItemId": "SGR60000851",
                                "type": "TRUCK",
                                "deliveryPrice": {"inclTax": 1399, "exclTax": 1165.83},
                                "deliveryItems": [
                                    {
                                        "itemNo": "90503662",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "60476349",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                ],
                                "possiblePickUpPoints": {
                                    "possiblePickUpPointMetadata": {
                                        "closestPickUpPointId": ""
                                    },
                                    "pickUpPoints": [
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "PARTIAL",
                                                "deliveryId": "",
                                                "deliveryType": "TRUCK",
                                                "selectableInfo": {"selectable": "YES"},
                                            },
                                            "price": {
                                                "inclTax": 1399,
                                                "exclTax": 1165.83,
                                            },
                                            "id": "",
                                            "name": "",
                                            "identifier": "",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "09:00-19:00",
                                            "openingHoursTueTime": "09:00-19:00",
                                            "openingHoursWedTime": "09:00-19:00",
                                            "openingHoursThuTime": "09:00-19:00",
                                            "openingHoursFriTime": "09:00-19:00",
                                            "openingHoursSatTime": "09:00-18:00",
                                            "openingHoursSunTime": "10:00-16:00",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 34.65,
                                            "timeWindows": {
                                                "metadata": {"available": True},
                                                "earliestPossibleSlot": {
                                                    "metadata": {
                                                        "timeZone": "Europe/Moscow",
                                                        "hasPriceDeviation": False,
                                                    },
                                                    "id": "",
                                                    "fromDateTime": "2022-01-21T09:00:00.000",
                                                    "toDateTime": "2022-01-21T18:00:00.000",
                                                },
                                            },
                                        },
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "PARTIAL",
                                                "deliveryId": "",
                                                "deliveryType": "TRUCK",
                                                "selectableInfo": {
                                                    "selectable": "UNCERTAIN",
                                                    "reason": [
                                                        "DELIVERY_TIME_WINDOW_NOT_EVALUATED"
                                                    ],
                                                },
                                            },
                                            "price": {
                                                "inclTax": 1399,
                                                "exclTax": 1165.83,
                                            },
                                            "id": "",
                                            "name": "",
                                            "identifier": "",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "08:00-19:00",
                                            "openingHoursTueTime": "08:00-19:00",
                                            "openingHoursWedTime": "08:00-19:00",
                                            "openingHoursThuTime": "08:00-19:00",
                                            "openingHoursFriTime": "08:00-19:00",
                                            "openingHoursSatTime": "09:00-16:00",
                                            "openingHoursSunTime": "09:00-16:00",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 2.98,
                                            "timeWindows": None,
                                        },
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "PARTIAL",
                                                "deliveryId": "",
                                                "deliveryType": "TRUCK",
                                                "selectableInfo": {
                                                    "selectable": "UNCERTAIN",
                                                    "reason": [
                                                        "DELIVERY_TIME_WINDOW_NOT_EVALUATED"
                                                    ],
                                                },
                                            },
                                            "price": {
                                                "inclTax": 1399,
                                                "exclTax": 1165.83,
                                            },
                                            "id": "",
                                            "name": "",
                                            "identifier": "identifier",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "09:00-18:00",
                                            "openingHoursTueTime": "09:00-18:00",
                                            "openingHoursWedTime": "09:00-18:00",
                                            "openingHoursThuTime": "09:00-18:00",
                                            "openingHoursFriTime": "09:00-18:00",
                                            "openingHoursSatTime": "09:00-16:00",
                                            "openingHoursSunTime": "",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 4.12,
                                            "timeWindows": None,
                                        },
                                    ],
                                },
                            }
                        ],
                    },
                    "unavailableItems": [
                        {
                            "id": "18",
                            "lineId": "18",
                            "itemNo": "80357835",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "10",
                            "lineId": "10",
                            "itemNo": "40363013",
                            "type": "ART",
                            "requiredQuantity": 1,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "1"
                            },
                        },
                        {
                            "id": "6",
                            "lineId": "6",
                            "itemNo": "20394949",
                            "type": "ART",
                            "requiredQuantity": 4,
                            "availableQuantity": 0,
                            "unavailableReason": "OP_NOT_ENOUGH_PROD_CHOICES",
                            "unavailableReasonCodeMap": {
                                "OP_NOT_ENOUGH_PROD_CHOICES": "4"
                            },
                        },
                    ],
                },
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["DELIVERY_ARRANGEMENT_UNAVAILABLE"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "PUOP",
                    "errors": [
                        {
                            "type": "INTEGRATION_APP_ERROR",
                            "service": "DELIVERY_ARRANGEMENTS",
                            "errorDetail": {
                                "errorCode": "EXTN_SOMOP_0015",
                                "errorDescription": "No PickUp Point Returned For ZipCode",
                                "errorUniqueExceptionId": "",
                            },
                        }
                    ],
                },
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["DELIVERY_ARRANGEMENT_UNAVAILABLE"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "CLICK_COLLECT_STORE",
                    "errors": [
                        {
                            "type": "INTEGRATION_APP_ERROR",
                            "service": "DELIVERY_ARRANGEMENTS",
                            "errorDetail": {
                                "errorCode": "EXTN_SOMOP_0015",
                                "errorDescription": "No PickUp Point Returned For ZipCode",
                                "errorUniqueExceptionId": "",
                            },
                        }
                    ],
                },
            ],
        },
    },
    {
        "context": {
            "retailUnit": "ru",
            "exclTaxCountry": False,
            "checkoutId": "",
            "currency": "RUB",
            "scope": {
                "type": "COLLECT",
                "subTypes": [
                    {"id": "PUP", "maxCollectionPoints": "40"},
                    {"id": "PUOP", "maxCollectionPoints": "20"},
                    {"id": "CLICK_COLLECT_STORE", "maxCollectionPoints": "10"},
                ],
            },
            "config": {
                "enableLeadTimeOrchestration": True,
                "enablePrimeTimeCalculation": True,
                "allowedPTSDeliveries": [
                    "HOME_DELIVERY_STANDARD",
                    "HOME_DELIVERY_CURBSIDE",
                    "HOME_DELIVERY_EXPRESS",
                    "HOME_DELIVERY_EXPRESS_CURBSIDE",
                ],
            },
            "businessUnit": {"code": "149", "type": "SIO"},
            "customerContext": {"customerType": "PRIVATE"},
            "capability": {
                "wheelChair": False,
                "rangeOfDays": True,
                "authToLeave": True,
            },
        },
        "possibleDeliveryServices": {
            "metadata": {
                "canAtLeastOneSolutionFulfillEntireCart": True,
                "expiryTime": "2021-12-26T18:56:10.957Z",
            },
            "deliveryServices": [
                {
                    "metadata": {
                        "selectableInfo": {"selectable": "YES"},
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "PUP",
                    "fulfillmentPossibility": "FULL",
                    "solutionId": "PUP~1~STANDARD",
                    "solution": "STANDARD",
                    "solutionPrice": {"inclTax": 399, "exclTax": 332.5},
                    "expiryTime": "2021-12-26T18:56:10.957Z",
                    "possibleDeliveries": {
                        "metadata": {"multipleDeliveries": False},
                        "deliveries": [
                            {
                                "id": "",
                                "metadata": {"rangeOfDays": False},
                                "fulfillmentDeliveryId": "PUP~~~2",
                                "serviceItemId": "SGR00000854",
                                "type": "PARCEL",
                                "deliveryPrice": {"inclTax": 399, "exclTax": 332.5},
                                "deliveryItems": [
                                    {
                                        "itemNo": "30480178",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                    {
                                        "itemNo": "10442682",
                                        "itemType": "ART",
                                        "quantity": 1,
                                        "shipNode": "CDC.049",
                                        "parentId": None,
                                    },
                                ],
                                "possiblePickUpPoints": {
                                    "possiblePickUpPointMetadata": {
                                        "closestPickUpPointId": ""
                                    },
                                    "pickUpPoints": [
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "FULL",
                                                "deliveryId": "",
                                                "deliveryType": "PARCEL",
                                                "selectableInfo": {"selectable": "YES"},
                                            },
                                            "price": {"inclTax": 399, "exclTax": 332.5},
                                            "id": "",
                                            "name": "myname",
                                            "identifier": "identifier",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "09:00-21:00",
                                            "openingHoursTueTime": "09:00-21:00",
                                            "openingHoursWedTime": "09:00-21:00",
                                            "openingHoursThuTime": "09:00-21:00",
                                            "openingHoursFriTime": "09:00-21:00",
                                            "openingHoursSatTime": "09:00-21:00",
                                            "openingHoursSunTime": "09:00-21:00",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 0.59,
                                            "timeWindows": {
                                                "metadata": {"available": True},
                                                "earliestPossibleSlot": {
                                                    "metadata": {
                                                        "timeZone": "Europe/Moscow",
                                                        "hasPriceDeviation": False,
                                                    },
                                                    "id": "",
                                                    "fromDateTime": "2022-01-07T10:00:00.000",
                                                    "toDateTime": "2022-01-07T20:00:00.000",
                                                },
                                            },
                                        },
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "FULL",
                                                "deliveryId": "",
                                                "deliveryType": "PARCEL",
                                                "selectableInfo": {
                                                    "selectable": "UNCERTAIN",
                                                    "reason": [
                                                        "DELIVERY_TIME_WINDOW_NOT_EVALUATED"
                                                    ],
                                                },
                                            },
                                            "price": {"inclTax": 399, "exclTax": 332.5},
                                            "id": "",
                                            "name": "",
                                            "identifier": "russianpost",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "09:00-21:00",
                                            "openingHoursTueTime": "09:00-21:00",
                                            "openingHoursWedTime": "09:00-21:00",
                                            "openingHoursThuTime": "09:00-21:00",
                                            "openingHoursFriTime": "09:00-21:00",
                                            "openingHoursSatTime": "09:00-21:00",
                                            "openingHoursSunTime": "09:00-21:00",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 0.69,
                                            "timeWindows": None,
                                        },
                                        {
                                            "ocPUPId": "",
                                            "metadata": {
                                                "deliveryServiceId": "",
                                                "deliveryServiceSolution": "STANDARD",
                                                "deliveryServiceFulfillmentMethodType": "PUP",
                                                "deliveryServiceFulfillmentPossibility": "FULL",
                                                "deliveryId": "",
                                                "deliveryType": "PARCEL",
                                                "selectableInfo": {
                                                    "selectable": "UNCERTAIN",
                                                    "reason": [
                                                        "DELIVERY_TIME_WINDOW_NOT_EVALUATED"
                                                    ],
                                                },
                                            },
                                            "price": {"inclTax": 399, "exclTax": 332.5},
                                            "id": "",
                                            "name": "",
                                            "identifier": "",
                                            "lsc": None,
                                            "latitude": "",
                                            "longitude": "",
                                            "openingHoursMonTime": "09:00-21:00",
                                            "openingHoursTueTime": "09:00-21:00",
                                            "openingHoursWedTime": "09:00-21:00",
                                            "openingHoursThuTime": "09:00-21:00",
                                            "openingHoursFriTime": "09:00-21:00",
                                            "openingHoursSatTime": "09:00-21:00",
                                            "openingHoursSunTime": "09:00-21:00",
                                            "country": "RU",
                                            "zipCode": "",
                                            "city": "",
                                            "state": None,
                                            "addressLine1": "",
                                            "addressLine2": "",
                                            "addressLine3": "",
                                            "addressLine4": "",
                                            "distance": 0.98,
                                            "timeWindows": None,
                                        },
                                    ],
                                },
                            }
                        ],
                    },
                },
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["DELIVERY_ARRANGEMENT_UNAVAILABLE"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "PUOP",
                    "errors": [
                        {
                            "type": "INTEGRATION_APP_ERROR",
                            "service": "DELIVERY_ARRANGEMENTS",
                            "errorDetail": {
                                "errorCode": "EXTN_SOMOP_0015",
                                "errorDescription": "No PickUp Point Returned For ZipCode",
                                "errorUniqueExceptionId": "",
                            },
                        }
                    ],
                },
                {
                    "metadata": {
                        "selectableInfo": {
                            "selectable": "NO",
                            "reason": ["DELIVERY_ARRANGEMENT_UNAVAILABLE"],
                        },
                        "serviceOfferCompatible": False,
                        "wheelChairCapability": False,
                        "slotBasedPricingEnabled": False,
                        "maxSolutionPrice": None,
                        "minSolutionPrice": None,
                        "deliveryPriceBasedOnPUPZipCode": False,
                    },
                    "id": "",
                    "deliveryArrangementsId": "",
                    "fulfillmentMethodType": "CLICK_COLLECT_STORE",
                    "errors": [
                        {
                            "type": "INTEGRATION_APP_ERROR",
                            "service": "DELIVERY_ARRANGEMENTS",
                            "errorDetail": {
                                "errorCode": "EXTN_SOMOP_0015",
                                "errorDescription": "No PickUp Point Returned For ZipCode",
                                "errorUniqueExceptionId": "",
                            },
                        }
                    ],
                },
            ],
        },
    },
]


@pytest.mark.parametrize("home", test_home_delivery_services_data)
@pytest.mark.parametrize("collect", test_collect_delivery_services_data)
def test_main(home: dict[str, Any], collect: dict[str, Any]):
    main(
        home_delivery_services_response=home,
        collect_delivery_services_response=collect,
    )
