from types import SimpleNamespace

import pytest

from ikea_api.wrappers._parsers.purchases import (
    get_history_datetime,
    parse_costs_order,
    parse_history,
    parse_status_banner_order,
)

status_banner = {
    "data": {
        "order": {
            "id": "111111111",
            "dateAndTime": {
                "time": "07:51:56Z",
                "date": "2021-11-18",
                "formattedLocal": "18 ноября 2021, 13:30",
                "formattedShortDate": "18.11.2021",
                "formattedLongDate": "18 ноября 2021",
                "formattedShortDateTime": "18.11.2021 13:30",
                "formattedLongDateTime": "18 ноября 2021, 13:30",
            },
            "status": "CREATED",
            "services": [],
            "deliveryMethods": [
                {
                    "id": "111111111",
                    "serviceId": "SGR90000897",
                    "status": "ORDER_RECEIVED",
                    "type": "TRUCK_CURBSIDE",
                    "deliveryDate": {
                        "actual": None,
                        "estimatedFrom": {
                            "time": "13:00:00Z",
                            "date": "2021-12-03",
                            "formattedLocal": "3 декабря 2021, 16:00",
                            "formattedShortDate": "03.12.2021",
                            "formattedLongDate": "3 декабря 2021",
                            "formattedShortDateTime": "03.12.2021 16:00",
                            "formattedLongDateTime": "3 декабря 2021, 16:00",
                        },
                        "estimatedTo": {
                            "time": "17:00:00Z",
                            "date": "2021-12-03",
                            "formattedLocal": "3 декабря 2021, 20:00",
                            "formattedShortDate": "03.12.2021",
                            "formattedLongDate": "3 декабря 2021",
                            "formattedShortDateTime": "03.12.2021 20:00",
                            "formattedLongDateTime": "3 декабря 2021, 20:00",
                        },
                        "dateTimeRange": "3 декабря 2021, 16:00—20:00",
                        "timeZone": "Europe/Moscow",
                    },
                }
            ],
        }
    }
}

costs = {
    "data": {
        "order": {
            "id": "111111111",
            "costs": {
                "total": {"code": "RUB", "value": 80000.0},
                "delivery": {"code": "RUB", "value": 3799.0},
                "service": None,
                "discount": None,
                "sub": {"code": "RUB", "value": 76201.0},
                "tax": {"code": "RUB", "value": 0.0},
                "taxRates": [
                    {
                        "percentage": "20",
                        "name": "VAT",
                        "amount": {"code": "RUB", "value": 15240.2},
                    }
                ],
            },
        }
    }
}
history = {
    "data": {
        "history": [
            {
                "id": "11111111",
                "dateAndTime": {
                    "time": "10:12:00Z",
                    "date": "2021-04-19",
                    "formattedLocal": "19.04.2021",
                    "formattedShortDate": "19.04.2021",
                    "formattedLongDate": "19 апреля 2021",
                    "formattedShortDateTime": "19.04.2021 13:12",
                    "formattedLongDateTime": "19 апреля 2021, 13:12",
                },
                "status": "IN_PROGRESS",
                "storeName": "IKEA",
                "totalCost": {"code": "RUB", "value": 8326.0},
            },
            {
                "id": "111111110",
                "dateAndTime": {
                    "time": "18:16:25Z",
                    "date": "2021-04-14",
                    "formattedLocal": "14.04.2021",
                    "formattedShortDate": "14.04.2021",
                    "formattedLongDate": "14 апреля 2021",
                    "formattedShortDateTime": "14.04.2021 21:16",
                    "formattedLongDateTime": "14 апреля 2021, 21:16",
                },
                "status": "COMPLETED",
                "storeName": "IKEA",
                "totalCost": {"code": None, "value": None},
            },
        ]
    }
}


def test_parse_status_banner_order():
    parse_status_banner_order(status_banner)


def test_parse_costs_order():
    parse_costs_order(costs)


@pytest.mark.parametrize(
    ("date", "time"), (("val1", "val2"), ("2021-04-14", "18:16:25Z"))
)
def test_get_history_datetime(date: str, time: str):
    assert (
        get_history_datetime(
            SimpleNamespace(dateAndTime=SimpleNamespace(date=date, time=time))  # type: ignore
        )
        == f"{date}T{time}"
    )


def test_parse_history():
    parse_history(history)
