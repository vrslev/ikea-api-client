from dataclasses import dataclass, field
from typing import Any

from ikea_api._endpoints.cart import Queries
from new import abc
from new.constants import Constants, extend_default_headers, get_headers_with_token


def get_session_data(constants: Constants) -> abc.SessionInfo:
    headers = extend_default_headers(
        {"X-Client-Id": "66e4684a-dbcb-499c-8639-a72fa50ac0c3"}, constants
    )
    url = "https://cart.oneweb.ingka.com/graphql"
    return abc.SessionInfo(base_url=url, headers=headers)


@dataclass
class Data:
    token: str
    query: str
    variables: dict[str, Any] = field(default_factory=dict)


class Endpoint(abc.Endpoint[Data, dict[str, Any]]):
    @staticmethod
    def prepare_request(data: Data):
        return abc.RequestInfo(
            method="POST",
            url="",
            json={"query": data.query, "variables": data.variables},
            headers=get_headers_with_token(data.token),
        )

    @staticmethod
    def parse_response(response: abc.ResponseInfo[Data, Any]):
        return response.json


def get_run_info(data: Data):
    return abc.RunInfo(get_session_data, Endpoint, data)


def show(token: str):
    return get_run_info(Data(token=token, query=Queries.cart))


class Fragments:
    item_props = """
    fragment ItemProps on Item {
        itemNo
        quantity
        type
        fees {
            weee
            eco
        }
        isFamilyItem
        childItems {
            itemNo
        }
        regularPrice {
            unit {
                inclTax
                exclTax
                tax
                validFrom
                validTo
                isLowerPrice
                isTimeRestrictedOffer
                previousPrice {
                    inclTax
                    exclTax
                    tax
                }
            }
            subTotalExclDiscount {
                inclTax
                exclTax
                tax
            }
            subTotalInclDiscount {
                inclTax
                exclTax
                tax
            }
            subTotalDiscount {
                amount
            }
            discounts {
                code
                amount
                description
                kind
            }
        }
        familyPrice {
            unit {
                inclTax
                exclTax
                tax
                validFrom
                validTo
            }
            subTotalExclDiscount {
                inclTax
                exclTax
                tax
            }
            subTotalInclDiscount {
                inclTax
                exclTax
                tax
            }
            subTotalDiscount {
                amount
            }
            discounts {
                code
                amount
                description
                kind
            }
        }
    }
    """

    product_props = """
    fragment ProductProps on Product {
        name
        globalName
        isNew
        category
        description
        isBreathTaking
        formattedItemNo
        displayUnit {
            type
            imperial {
                unit
                value
            }
            metric {
                unit
                value
            }
        }
        unitCode
        measurements {
            metric
            imperial
        }
        technicalDetails {
            labelUrl
        }
        images {
            url
            quality
            width
        }
    }
    """

    totals = """
    fragment Totals on Cart {
        regularTotalPrice {
            totalExclDiscount {
                inclTax
                exclTax
                tax
            }
            totalInclDiscount {
                inclTax
                exclTax
                tax
            }
            totalDiscount {
                amount
            }
            totalSavingsDetails {
                familyDiscounts
            }
        }
        familyTotalPrice {
            totalExclDiscount {
                inclTax
                exclTax
                tax
            }
            totalInclDiscount {
                inclTax
                exclTax
                tax
            }
            totalDiscount {
                amount
            }
            totalSavingsDetails {
                familyDiscounts
            }
            totalSavingsInclDiscount {
                amount
            }
        }
    }
    """

    cart_props = """
    fragment CartProps on Cart {{
        currency
        checksum
        context {{
            userId
            isAnonymous
            retailId
        }}
        coupon {{
            code
            validFrom
            validTo
            description
        }}
        items {{
        ...ItemProps
            product {{
            ...ProductProps
            }}
        }}
        ...Totals
    }}
    {}
    {}
    {}
    """.format(
        item_props,
        product_props,
        totals,
    )


class Queries:
    cart = """
    query Cart(
        $languageCode: String
    ) {
        cart(languageCode: $languageCode) {
        ...CartProps
        }
    }
  %s
    """ % (
        Fragments.cart_props
    )
