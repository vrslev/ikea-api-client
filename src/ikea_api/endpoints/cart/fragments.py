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


cart_props = f"""
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
  {item_props}
  {product_props}
  {totals}
"""
