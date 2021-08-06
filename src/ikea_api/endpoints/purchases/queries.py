from .fragments import (
    costs,
    date_and_time,
    delivery_date,
    delivery_info,
    product,
    service_info,
)

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
    date_and_time
)


status_banner_order = f"""
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

  {date_and_time}
  {delivery_date}
  {service_info}
  {delivery_info}
"""


costs_order = """
  query CostsOrder($orderNumber: String!, $liteId: String) {{
    order(orderNumber: $orderNumber, liteId: $liteId) {{
      id
      costs {{
        ...Costs
      }}
    }}
  }}

  {}

""".format(
    costs,
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
    product
)
