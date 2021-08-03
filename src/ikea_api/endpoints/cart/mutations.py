from .fragments import cart_props

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
    cart_props
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
    cart_props
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
    cart_props
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
    cart_props
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
    cart_props
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
    cart_props
)
