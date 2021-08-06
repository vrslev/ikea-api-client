#
# StatusBannerOrder
#

# also History
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


#
# CostsOrder
#

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


#
# ProductListOrder
#

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
