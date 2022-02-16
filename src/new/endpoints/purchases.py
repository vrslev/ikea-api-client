from typing import Any, Literal

from new.abc import BaseAPI, Endpoint, SessionInfo, add_handler
from new.constants import Constants, get_headers_with_token
from new.error_handlers import handle_401, handle_graphql_error


def _build_payload(operation_name: str, query: str, **variables: Any) -> dict[str, Any]:
    return {"operationName": operation_name, "variables": variables, "query": query}


class API(BaseAPI):
    token: str

    def __init__(self, constants: Constants, *, token: str) -> None:
        self.token = token
        super().__init__(constants)

    def get_session_info(self) -> SessionInfo:
        url = "https://purchase-history.ocp.ingka.ikea.com/graphql"
        headers = self.extend_default_headers(
            {
                "Accept": "*/*",
                "Accept-Language": f"{self.const.language}-{self.const.country}",
                "Origin": "https://order.ikea.com",
                "Referer": f"https://order.ikea.com/{self.const.country}/{self.const.language}/purchases/",
                **get_headers_with_token(self.token),
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @add_handler(handle_graphql_error)
    @add_handler(handle_401)
    def history(self, *, take: int = 5, skip: int = 0) -> Endpoint[dict[str, Any]]:
        """Get purchase history.
        Parameters are for pagination. If you want to see all your purchases set 'take' to 10000.
        """
        payload = _build_payload("History", Queries.history, take=take, skip=skip)
        response = yield self.RequestInfo("POST", "", json=payload)
        return response.json

    @add_handler(handle_graphql_error)
    @add_handler(handle_401)
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
    ) -> Endpoint[list[dict[str, Any]]]:
        """Get order information: status and costs.

        :params order_number: Purchase ID
        :params email: Email. If set, there's no need to get token.
        :params queries: Queries that will be included in request
        :params skip_products: Relevant to ProductListOrder
        :params skip_product_prices: Relevant to ProductListOrder
        :params take_products: Relevant to ProductListOrder
        """
        payload: list[dict[str, Any]] = []

        if "StatusBannerOrder" in queries:
            payload.append(
                _build_payload(
                    "StatusBannerOrder",
                    Queries.status_banner_order,
                    orderNumber=order_number,
                )
            )
        if "CostsOrder" in queries:
            payload.append(
                _build_payload(
                    "CostsOrder", Queries.costs_order, orderNumber=order_number
                )
            )
        if "ProductListOrder" in queries:
            payload.append(
                _build_payload(
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
            for chunk in payload:
                chunk["variables"]["liteId"] = email

            headers = {
                "Referer": f"https://order.ikea.com/{self.const.country}/"
                + f"{self.const.language}/purchases/lookup"
            }
        else:
            headers = {"Referer": f"https://order.ikea.com/{order_number}/"}

        response = yield self.RequestInfo("POST", "", json=payload, headers=headers)
        return response.json


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
