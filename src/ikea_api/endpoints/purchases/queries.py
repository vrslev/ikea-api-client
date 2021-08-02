from .fragments import *

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
      }
    }
  }

  %s
""" % (
    date_and_time
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
    date_and_time,
    delivery_date,
    service_info,
    delivery_info,
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
    costs
)
