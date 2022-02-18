from typing import Any, TypedDict

from new.abc import BaseAPI, EndpointGen, SessionInfo, endpoint
from new.constants import Constants, get_headers_with_token
from new.error_handlers import handle_401, handle_graphql_error


class _TemplatedItem(TypedDict):
    itemNo: str
    quantity: int


def _convert_items(items: dict[str, int]) -> list[_TemplatedItem]:
    return [{"itemNo": item_code, "quantity": qty} for item_code, qty in items.items()]


class API(BaseAPI):
    token: str

    def __init__(self, constants: Constants, *, token: str) -> None:
        self.token = token
        super().__init__(constants)

    def get_session_info(self) -> SessionInfo:
        url = "https://cart.oneweb.ingka.com/graphql"
        headers = self.extend_default_headers(
            {
                "X-Client-Id": "66e4684a-dbcb-499c-8639-a72fa50ac0c3",
                **get_headers_with_token(self.token),
            }
        )
        return SessionInfo(base_url=url, headers=headers)

    @endpoint(handlers=[handle_graphql_error, handle_401])
    def _req(self, query: str, **variables: Any) -> EndpointGen[dict[str, Any]]:
        payload = {
            "query": query,
            "variables": {"languageCode": self.const.language, **variables},
        }
        response = yield self.RequestInfo("POST", "", json=payload)
        return response.json

    def show(self):
        return self._req(Queries.cart)

    def clear(self):
        return self._req(Mutations.clear_items)

    def add_items(self, items: dict[str, int]):
        """
        Add items to cart.
        Required items list format: {'item_no': quantity, ...}
        """
        return self._req(Mutations.add_items, items=_convert_items(items))

    def update_items(self, items: dict[str, int]):
        """
        Replace quantity for given item to the new one.
        Required items list format: {'item_no': quantity, ...}
        """
        return self._req(Mutations.update_items, items=_convert_items(items))

    def copy_items(self, *, source_user_id: str):
        """Copy cart from another account."""
        return self._req(Mutations.copy_items, sourceUserId=source_user_id)

    def remove_items(self, item_codes: list[str]):
        """Remove items by item codes."""
        return self._req(Mutations.remove_items, itemNos=item_codes)

    def set_coupon(self, code: str):
        return self._req(Mutations.set_coupon, code=code)

    def clear_coupon(self):
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
