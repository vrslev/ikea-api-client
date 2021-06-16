from . import fragments


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
""" % (fragments.date_and_time)


status_banner_order = """
  query StatusBannerOrder($orderNumber: String!, $liteId: String) {
    order(orderNumber: $orderNumber, liteId: $liteId) {
      id
      dateAndTime {
        ...DateAndTime
      }
      status
      services {
        ...ServiceInfo
      }
      deliveryMethods {
        ...DeliveryInfo
      }
    }
  }

  %s
  %s
  %s
  %s
""" % (fragments.date_and_time, fragments.delivery_date,
       fragments.service_info, fragments.delivery_info)


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
""" % (fragments.costs)