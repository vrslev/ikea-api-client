import re
import json
import requests

CONFIG = json.loads(open('config.json', 'r').read())
STORAGE = json.loads(open('storage.json', 'r').read())

HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Origin': 'https://www.ikea.com',
    'Referer': 'https://www.ikea.com/'
}

class Cart:
    """
    Can show, clear a cart, add or delete items, get delivery options.
    """
    def __init__(self, token):
        self.token = token
        self.endpoint = 'https://cart.oneweb.ingka.com/graphql'
        self.headers = HEADERS
        self.headers |= {
            'Host': 'cart.oneweb.ingka.com',
            'Authorization': 'Bearer ' + token,
            'X-Client-Id': '66e4684a-dbcb-499c-8639-a72fa50ac0c3'
        }
        self.cart_graphql_props = ' {\n      ...CartProps\n    }\n  }\n  \n  fragment CartProps on Cart {\n    currency\n    checksum\n    context {\n      userId\n      isAnonymous\n      retailId\n    }\n    coupon {\n      code\n      validFrom\n      validTo\n      description\n    }\n    items {\n      ...ItemProps\n      product {\n        ...ProductProps\n      }\n    }\n    ...Totals\n  }\n  \nfragment ItemProps on Item {\n  itemNo\n  quantity\n  type\n  fees {\n    weee\n    eco\n  }\n  isFamilyItem\n  childItems {\n    itemNo\n  }\n  regularPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n      isLowerPrice\n      isTimeRestrictedOffer\n      previousPrice {\n        inclTax\n        exclTax\n        tax\n      }\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n  familyPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n}\n\n  \n  fragment ProductProps on Product {\n    name\n    globalName\n    isNew\n    category\n    description\n    isBreathTaking\n    formattedItemNo\n    displayUnit {\n      type\n      imperial {\n        unit\n        value\n      }\n      metric {\n        unit\n        value\n      }\n    }\n    measurements {\n      metric\n      imperial\n    }\n    technicalDetails {\n      labelUrl\n    }\n    images {\n      url\n      quality\n      width\n    }\n  }\n\n  \n  fragment Totals on Cart {\n    regularTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n    }\n    familyTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n      totalSavingsInclDiscount {\n        amount\n      }\n    }\n  }\n\n\n'

    def show(self):
        data = {'query': '\n  query Cart(\n    $languageCode: String\n    ) '
                + '{\n    cart(languageCode: $languageCode) ' + self.cart_graphql_props,
                'variables': {'languageCode': 'ru'}}
        response = requests.post(self.endpoint, headers=self.headers, json=data)
        return response.json()

    def clear(self):
        data = {'query':'\n  mutation ClearItems(\n    $languageCode: String\n  ) '
                + '{\n    clearItems(languageCode: $languageCode) ' + self.cart_graphql_props,
                'variables': {'languageCode': 'ru'}}
        response = requests.post(self.endpoint, headers=self.headers, json=data)
        return response.json()

    def add_items(self, items):
        items_templated = []
        for item in items:
            items_templated.append('{itemNo: "%s", quantity: %d}' % (item, items[item]))
        data = {'query':'mutation {addItems(items: ['
        + ', '.join(items_templated) + ']) {quantity}}'}
        response = requests.post(self.endpoint, headers=self.headers, json=data)
        return response.json()

    def delete_items(self, items):
        # Required format of items:
        # 'item_no': quantity
        items_str = []
        for item in items:
            items_str.append(str(item))
        data = {'query': '\n  mutation RemoveItems(\n    $itemNos: [ID!]!\n    $languageCode: ' \
                + 'String\n  ){\n    removeItems(itemNos: $itemNos, languageCode: $languageCode) '
                + self.cart_graphql_props,
                'variables': {
                    'itemNos': items,
                    'languageCode': 'ru'
                }}
        response = requests.post(self.endpoint, headers=self.headers, json=data)
        return response.json()


    def fetch_delivery_options(self):
        zip_code = CONFIG['zip_code']
        if not zip_code:
            raise Exception('Add zip code in config.json')

        endpoint = 'https://ordercapture.ikea.ru/ordercaptureapi/ru/checkouts'
        headers = HEADERS
        headers |= {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Host': 'ordercapture.ikea.ru',
            'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
        }
        def get_checkout():
            data = {'shoppingType':'ONLINE','channel':'WEBAPP','checkoutType':'STANDARD',
            'languageCode':'ru','preferredServiceType':None,'requestedServiceTypes':None}
            response = requests.post(endpoint, headers=headers, json=data, verify=False)
            try:
                return response.json()['resourceId']
            except KeyError as exc:
                raise Exception('Cart is empty') from exc

        def get_delivery_area(checkout):
            url = '%s/%s/delivery-areas' % (endpoint, checkout)
            data = {'zipCode': CONFIG['zip_code'], 'enableRangeOfDays': False}
            response = requests.post(url, headers=headers, json=data, verify=False)
            return response.json()['resourceId']

        def get_delivery_services():
            checkout = get_checkout()
            delivery_area = get_delivery_area(checkout)
            url = '%s/%s/delivery-areas/%s/delivery-services' % (endpoint, checkout, delivery_area)
            response = requests.get(url, headers=headers, verify=False)
            return response.json()

        return get_delivery_services()

    def parse_delivery_options(self, options):
        parsed_options = []
        for option in options:
            try:
                price = option['servicePrice']['amount']
                price = int(re.search(r'(\d+)(.00)?', price)[1])
                date_info = option['deliveries'][0]['selectedTimeWindow']
                from_date_time = date_info['fromDateTime']
                to_date_time = date_info['fromDateTime']
            except TypeError as exc:
                try:
                    raise Exception(options['message']) from exc
                except TypeError as exc:
                    raise Exception(option['errorMessage']['errorDescription']) from exc

            try:
                unavailable_items = []
                for item in option['unavailableItems']:
                    unavailable_items.append({
                        'item_no': item['itemNo'],
                        'is_combination': item['type'] != 'ART',
                        'required_qty': item['requiredQuantity'],
                        'available_qty': item['availableQuantity']
                    })
            except TypeError:
                unavailable_items = []
            parsed_option = {
                'delivery_id': option['id'],
                'type': option['fulfillmentMethodType'],
                'service_type': option['servicetype'],
                'from_date_time': from_date_time,
                'to_date_time': to_date_time,
                'price': price,
                'unavailable_items': unavailable_items
            }
            parsed_options.append(parsed_option)
        return parsed_options

    def get_delivery_options(self):
        src = self.fetch_delivery_options()
        res = self.parse_delivery_options(src)
        return res