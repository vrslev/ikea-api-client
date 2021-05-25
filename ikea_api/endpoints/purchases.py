from ..api import Api


class Purchases(Api):
    def __init__(self, token):
        super().__init__(token, 'https://purchase-history.ocp.ingka.ikea.com/graphql')
        origin = 'https://order.ikea.com'
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': '{}-{}'.format(self.language_code, self.country_code),
            'Origin': origin,
            'Referer': '{}/{}/{}/purchases/'.format(
                origin, self.country_code, self.language_code)
        })

    def purchase_history(self):
        payload = {
            "operationName": "History",
            "variables": {
                "take": 5,
                "skip": 0
            },
            "query": "query History($skip: Int!, $take: Int!) {\n  history(skip: $skip, take: $take) {\n    id\n    dateAndTime {\n      ...DateAndTime\n      __typename\n    }\n    status\n    storeName\n    totalCost {\n      code\n      value\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment DateAndTime on DateAndTime {\n  time\n  date\n  formattedLocal\n  formattedShortDate\n  formattedLongDate\n  formattedShortDateTime\n  formattedLongDateTime\n  __typename\n}\n"
        }
        return self.call_api(data=payload)

    def purchase_info(self, purchase_id, email=None):
        headers = {
            'Referer': '{}/{}/'.format(self.session.headers['Origin'], purchase_id)
        }
        payload = [
            {
                "operationName": "StatusBannerOrder",
                "variables": {
                    "orderNumber": purchase_id,
                    "receiptNumber": ""
                },
                "query": "query StatusBannerOrder($orderNumber: String!, $liteId: String) {\n  order(orderNumber: $orderNumber, liteId: $liteId) {\n    id\n    dateAndTime {\n      ...DateAndTime\n      __typename\n    }\n    status\n    services {\n      ...ServiceInfo\n      __typename\n    }\n    deliveryMethods {\n      ...DeliveryInfo\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment DateAndTime on DateAndTime {\n  time\n  date\n  formattedLocal\n  formattedShortDate\n  formattedLongDate\n  formattedShortDateTime\n  formattedLongDateTime\n  __typename\n}\n\nfragment ServiceInfo on Service {\n  id\n  status\n  date {\n    ...DeliveryDate\n    __typename\n  }\n  __typename\n}\n\nfragment DeliveryDate on DeliveryDate {\n  actual {\n    ...DateAndTime\n    __typename\n  }\n  estimatedFrom {\n    ...DateAndTime\n    __typename\n  }\n  estimatedTo {\n    ...DateAndTime\n    __typename\n  }\n  dateTimeRange\n  timeZone\n  __typename\n}\n\nfragment DeliveryInfo on DeliveryMethod {\n  id\n  serviceId\n  status\n  type\n  deliveryDate {\n    ...DeliveryDate\n    __typename\n  }\n  __typename\n}\n"
            },
            {
                "operationName": "CostsOrder",
                "variables": {
                    "orderNumber": purchase_id,
                    "receiptNumber": ""
                },
                "query": "query CostsOrder($orderNumber: String!, $liteId: String) {\n  order(orderNumber: $orderNumber, liteId: $liteId) {\n    id\n    costs {\n      ...Costs\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Costs on Costs {\n  total {\n    ...Money\n    __typename\n  }\n  delivery {\n    ...Money\n    __typename\n  }\n  service {\n    ...Money\n    __typename\n  }\n  discount {\n    ...Money\n    __typename\n  }\n  sub {\n    ...Money\n    __typename\n  }\n  tax {\n    ...Money\n    __typename\n  }\n  taxRates {\n    ...TaxRate\n    __typename\n  }\n  __typename\n}\n\nfragment Money on Money {\n  code\n  value\n  __typename\n}\n\nfragment TaxRate on TaxRate {\n  percentage\n  name\n  amount {\n    ...Money\n    __typename\n  }\n  __typename\n}\n"
            }
        ]

        if email:
            headers['Referer'] = self.session.headers['Referer'] + 'lookup'
            for d in payload:
                d['variables']['liteId'] = email

        return self.call_api(data=payload, headers=headers)
