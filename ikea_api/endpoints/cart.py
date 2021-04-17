from ..api import Api
from ..utils import parse_item_code
from ..errors import WrongItemCodeError


class Cart(Api):
    """
    Can show, clear a cart, add or delete items, get delivery options.
    """

    def __init__(self, token):
        super().__init__(token, 'https://cart.oneweb.ingka.com/graphql')
        self.session.headers.update({
            'Accept-Language': 'ru',
            'Origin': 'https://www.ikea.com',
            'Referer': 'https://www.ikea.com/',
            'X-Client-Id': '66e4684a-dbcb-499c-8639-a72fa50ac0c3'
        })
        self.cart_graphql_props = ' {\n      ...CartProps\n    }\n  }\n  \n  fragment CartProps on Cart {\n    currency\n    checksum\n    context {\n      userId\n      isAnonymous\n      retailId\n    }\n    coupon {\n      code\n      validFrom\n      validTo\n      description\n    }\n    items {\n      ...ItemProps\n      product {\n        ...ProductProps\n      }\n    }\n    ...Totals\n  }\n  \nfragment ItemProps on Item {\n  itemNo\n  quantity\n  type\n  fees {\n    weee\n    eco\n  }\n  isFamilyItem\n  childItems {\n    itemNo\n  }\n  regularPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n      isLowerPrice\n      isTimeRestrictedOffer\n      previousPrice {\n        inclTax\n        exclTax\n        tax\n      }\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n  familyPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n}\n\n  \n  fragment ProductProps on Product {\n    name\n    globalName\n    isNew\n    category\n    description\n    isBreathTaking\n    formattedItemNo\n    displayUnit {\n      type\n      imperial {\n        unit\n        value\n      }\n      metric {\n        unit\n        value\n      }\n    }\n    measurements {\n      metric\n      imperial\n    }\n    technicalDetails {\n      labelUrl\n    }\n    images {\n      url\n      quality\n      width\n    }\n  }\n\n  \n  fragment Totals on Cart {\n    regularTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n    }\n    familyTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n      totalSavingsInclDiscount {\n        amount\n      }\n    }\n  }\n\n\n'

    def show(self):
        """Show items in cart"""
        data = {
            'query': '\n  query Cart(\n    $languageCode: String\n    ) '
            + '{\n    cart(languageCode: $languageCode) ' +
            self.cart_graphql_props,
            'variables': {
                'languageCode': 'ru'
            }
        }
        return self.call_api(data=data)

    def clear(self):
        """Delete all items from cart"""
        data = {
            'query': '\n  mutation ClearItems(\n    $languageCode: String\n  ) '
            + '{\n    clearItems(languageCode: $languageCode) ' +
            self.cart_graphql_props,
            'variables': {
                'languageCode': 'ru'
            }
        }
        return self.call_api(data=data)

    def add_items(self, items):
        """
        Add items to cart.
        Required items list format: [{'item_no': quantity, ...}]
        """
        items_templated = []
        for item in items:
            item = parse_item_code(item)
            if item:
                items_templated.append(
                '{itemNo: "%s", quantity: %s}' % (item, items[item]))
        data = {'query': 'mutation {addItems(items: ['
                + ', '.join(items_templated) + ']) {quantity}}'}
        response = self.call_api(data=data)
        try:
            error = response['errors'][0]['extensions']['code']
            # TODO: Check for known errors in utils.py all self.call_api()
            if response['errors'][0]['extensions']['code'] == 'INVALID_ITEM_NUMBER' and response['errors'][0]['extensions']['data']['itemNos']:
                raise WrongItemCodeError(
                    response['errors'][0]['extensions']['data']['itemNos'])
        except KeyError:
            return response

    def delete_items(self, items):
        """Delete items from cart."""
        items_parsed = parse_item_code(items)
        data = {
            'query': '\n  mutation RemoveItems(\n    $itemNos: [ID!]!\n    $languageCode: '
            + 'String\n  ){\n    removeItems(itemNos: $itemNos, languageCode: $languageCode) ' +
            self.cart_graphql_props,
            'variables': {
                'itemNos': items_parsed,
                'languageCode': 'ru'
            }
        }
        return self.call_api(data=data)
