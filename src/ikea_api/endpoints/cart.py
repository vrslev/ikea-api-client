from __future__ import annotations

from typing import Any, TypedDict

from ikea_api.abc import Endpoint, EndpointInfo, SessionInfo, endpoint
from ikea_api.base_ikea_api import BaseAuthIkeaAPI
from ikea_api.error_handlers import (
    handle_401,
    handle_graphql_error,
    handle_json_decode_error,
    handle_not_success,
)


class _TemplatedItem(TypedDict):
    itemNo: str
    quantity: int


def convert_items(items: dict[str, int]) -> list[_TemplatedItem]:
    return [{"itemNo": item_code, "quantity": qty} for item_code, qty in items.items()]


class Cart(BaseAuthIkeaAPI):
    def _get_session_info(self) -> SessionInfo:
        url = "https://cart.oneweb.ingka.com/graphql"
        headers = self._extend_default_headers_with_auth(
            {"X-Client-Id": "66e4684a-dbcb-499c-8639-a72fa50ac0c3"}
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(
        handlers=[
            handle_json_decode_error,
            handle_graphql_error,
            handle_401,
            handle_not_success,
        ]
    )
    def _req(self, query: str, **variables: Any) -> Endpoint[dict[str, Any]]:
        payload = {
            "query": query,
            "variables": {"languageCode": self._const.language, **variables},
        }
        response = yield self._RequestInfo("POST", json=payload)
        return response.json

    def show(self) -> EndpointInfo[dict[str, Any]]:
        return self._req(Queries.cart)

    def clear(self) -> EndpointInfo[dict[str, Any]]:
        return self._req(Mutations.clear_items)

    def add_items(self, items: dict[str, int]) -> EndpointInfo[dict[str, Any]]:
        """
        Add items to cart.
        Required items list format: {'item_no': quantity, ...}
        """
        return self._req(Mutations.add_items, items=convert_items(items))

    def update_items(self, items: dict[str, int]) -> EndpointInfo[dict[str, Any]]:
        """
        Replace quantity for given item to the new one.
        Required items list format: {'item_no': quantity, ...}
        """
        return self._req(Mutations.update_items, items=convert_items(items))

    def copy_items(self, *, source_user_id: str) -> EndpointInfo[dict[str, Any]]:
        """Copy cart from another account."""
        return self._req(Mutations.copy_items, sourceUserId=source_user_id)

    def remove_items(self, item_codes: list[str]) -> EndpointInfo[dict[str, Any]]:
        """Remove items by item codes."""
        return self._req(Mutations.remove_items, itemNos=item_codes)

    def set_coupon(self, code: str) -> EndpointInfo[dict[str, Any]]:
        return self._req(Mutations.set_coupon, code=code)

    def clear_coupon(self) -> EndpointInfo[dict[str, Any]]:
        return self._req(Mutations.clear_coupon)


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


class Mutations:
    add_items = """
    mutation AddItems(
        $items: [AddItemInput!]!
        $languageCode: String
    ) {
        addItems(items: $items, languageCode: $languageCode) {
        quantity
            context {
                userId
                isAnonymous
                retailId
            }
        }
    }
    """

    clear_coupon = """
    mutation ClearCoupon(
        $languageCode: String
    ) {
        clearCoupon(languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
    )

    clear_items = """
    mutation ClearItems(
        $languageCode: String
    ) {
        clearItems(languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
    )

    copy_items = """
    mutation CopyItems(
        $sourceUserId: ID!
        $languageCode: String
    ) {
        copyItems(sourceUserId: $sourceUserId, languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
    )

    remove_items = """
    mutation RemoveItems(
        $itemNos: [ID!]!
        $languageCode: String
    ) {
        removeItems(itemNos: $itemNos, languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
    )

    set_coupon = """
    mutation SetCoupon(
        $code: String!
        $languageCode: String
    ) {
        setCoupon(code: $code, languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
    )

    update_items = """
    mutation UpdateItems(
        $items: [UpdateItemInput!]!
        $languageCode: String
    ) {
        updateItems(items: $items, languageCode: $languageCode) {
        ...CartProps
        }
    }

    %s
    """ % (
        Fragments.cart_props
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
