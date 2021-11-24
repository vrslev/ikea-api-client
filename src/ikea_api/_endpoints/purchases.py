from __future__ import annotations

import sys
from typing import Any

from ikea_api._api import CustomResponse, GraphQLAPI, GraphQLResponse
from ikea_api._constants import Constants
from ikea_api.exceptions import GraphQLError

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


class Purchases(GraphQLAPI):
    def __init__(self, token: str):
        super().__init__(
            endpoint="https://purchase-history.ocp.ingka.ikea.com/graphql", token=token
        )
        self._session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": f"{Constants.LANGUAGE_CODE}-{Constants.COUNTRY_CODE}",
                "Origin": "https://order.ikea.com",
                "Referer": f"https://order.ikea.com/{Constants.COUNTRY_CODE}/{Constants.LANGUAGE_CODE}/purchases/",
            }
        )

    def _build_payload(self, operation_name: str, query: str, **variables: Any):
        return {"operationName": operation_name, "variables": variables, "query": query}

    def history(self, *, take: int = 5, skip: int = 0):
        """Get purchase history.
        Parameters are for pagination. If you want to see all your purchases set 'take' to 10000.
        """
        payload = self._build_payload("History", Queries.history, take=take, skip=skip)
        return self._post(json=payload)

    def _error_handler(self, response: CustomResponse):
        if isinstance(response._json, list):  # from order_info
            dict_: GraphQLResponse
            for dict_ in response._json:  # type: ignore
                if "errors" in dict_:
                    raise GraphQLError(response)

    def order_info(
        self,
        order_number: str,
        *,
        email: str | None = None,
        queries: list[
            Literal["StatusBannerOrder", "CostsOrder", "ProductListOrder"]
        ] = ["StatusBannerOrder", "CostsOrder", "ProductListOrder"],
        skip_products: int = 0,
        skip_product_prices: bool = False,
        take_products: int = 10,
    ) -> list[GraphQLResponse]:
        """Get order information: status and costs.

        :params order_number: Purchase ID
        :params email: Email. If set, there's no need to get token.
        :params queries: Queries that will be included in request
        :params skip_products: Relevant to ProductListOrder
        :params skip_product_prices: Relevant to ProductListOrder
        :params take_products: Relevant to ProductListOrder
        """
        headers = {"Referer": f"{self._session.headers['Origin']}/{order_number}/"}
        payload: list[dict[str, Any]] = []

        if "StatusBannerOrder" in queries:
            payload.append(
                self._build_payload(
                    "StatusBannerOrder",
                    Queries.status_banner_order,
                    orderNumber=order_number,
                )
            )
        if "CostsOrder" in queries:
            payload.append(
                self._build_payload(
                    "CostsOrder",
                    Queries.costs_order,
                    orderNumber=order_number,
                )
            )
        if "ProductListOrder" in queries:
            payload.append(
                self._build_payload(
                    "ProductListOrder",
                    Queries.product_list_order,
                    orderNumber=order_number,
                    receiptNumber="",
                    skip=skip_products,
                    skipPrice=skip_product_prices,
                    take=take_products,
                )
            )

        if email:
            headers["Referer"] = self._session.headers["Referer"] + "lookup"
            for chunk in payload:
                chunk["variables"]["liteId"] = email

        return self._post(headers=headers, json=payload)  # type: ignore


class Fragments:
    date_and_time = """
    fragment DateAndTime on DateAndTime {
        time
        date
        formattedLocal
        formattedShortDate
        formattedLongDate
        formattedShortDateTime
        formattedLongDateTime
    }
    """

    delivery_date = """
    fragment DeliveryDate on DeliveryDate {
        actual {
        ...DateAndTime
        }
        estimatedFrom {
        ...DateAndTime
        }
        estimatedTo {
        ...DateAndTime
        }
        dateTimeRange
        timeZone
    }
    """

    service_info = """
    fragment ServiceInfo on Service {
        id
        status
        date {
        ...DeliveryDate
        }
    }
    """

    delivery_info = """
    fragment DeliveryInfo on DeliveryMethod {
        id
        serviceId
        status: status2
        type
        deliveryDate {
        ...DeliveryDate
        }
    }
    """

    money = """
    fragment Money on Money {
        code
        value
    }
    """

    tax_rate = """
    fragment TaxRate on TaxRate {
        percentage
        name
        amount {
        ...Money
        }
    }
    """

    costs = """
    fragment Costs on Costs {{
        total {{
        ...Money
        }}
        delivery {{
        ...Money
        }}
        service {{
        ...Money
        }}
        discount {{
        ...Money
        }}
        sub {{
        ...Money
        }}
        tax {{
        ...Money
        }}
        taxRates {{
        ...TaxRate
        }}
    }}
    {}
    {}
    """.format(
        money,
        tax_rate,
    )

    article = """
    fragment Article on Product {
        name
        description
        href
        quantity
        decimalQuantity
        priceUnitText
        id
        splitDelivery
        image {
            small
            medium
            large
        }
    }
    """

    product = """
    fragment Product on Product {
        ...Article
        unitPrice @skip(if: $skipPrice) {
            formatted
        }
        totalPrice @skip(if: $skipPrice) {
            formatted
        }
        assemblyRequired
    }
    %s
    """ % (
        article
    )


class Queries:
    history = """
    query History($skip: Int!, $take: Int!) {
        history(skip: $skip, take: $take) {
        id
        dateAndTime {
        ...DateAndTime
        }
        status
        storeName
            totalCost {
                code
                value
                formatted
            }
        }
    }

    %s
    """ % (
        Fragments.date_and_time
    )

    status_banner_order = """
    query StatusBannerOrder($orderNumber: String!, $liteId: String) {{
        order(orderNumber: $orderNumber, liteId: $liteId) {{
            id
            dateAndTime {{
            ...DateAndTime
            }}
            status
            services {{
            ...ServiceInfo
            }}
            deliveryMethods {{
                ...DeliveryInfo
            }}
        }}
    }}

    {}
    {}
    {}
    {}
    """.format(
        Fragments.date_and_time,
        Fragments.delivery_date,
        Fragments.service_info,
        Fragments.delivery_info,
    )

    costs_order = """
    query CostsOrder($orderNumber: String!, $liteId: String) {
        order(orderNumber: $orderNumber, liteId: $liteId) {
            id
            costs {
                ...Costs
            }
        }
    }

    %s

    """ % (
        Fragments.costs
    )

    product_list_order = """
    query ProductListOrder(
        $orderNumber: String!
        $liteId: String
        $skip: Int!
        $take: Int!
        $skipPrice: Boolean!
    ) {
        order(orderNumber: $orderNumber, liteId: $liteId) {
            id
            articles {
                ... on AnyDirectionProducts {
                    quantity
                    direction
                    any(skip: $skip, take: $take) {
                        ...Product
                    }
                }
                ... on ExchangeProducts {
                    numberOfInboundElements
                    numberOfOutboundElements
                    inboundQuantity
                    outboundQuantity
                    inbound(skip: $skip, take: $take) {
                    ...Product
                    }
                    outbound(skip: $skip, take: $take) {
                    ...Product
                    }
                }
            }
        }
    }

    %s
    """ % (
        Fragments.product
    )
