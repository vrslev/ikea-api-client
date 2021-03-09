import re
import json
import base64
import requests
from bs4 import BeautifulSoup
from authlib.oauth2.rfc7636 import create_s256_code_challenge
from authlib.common.security import generate_token

HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Origin': 'https://www.ikea.com',
    'Referer': 'https://www.ikea.com/'
}

def fetch_new_token():
    url = 'https://api.ingka.ikea.com/guest/token'
    headers = HEADERS
    headers |= {
        'Host': 'api.ingka.ikea.com',
        'X-Client-Id': 'e026b58d-dd69-425f-a67f-1e9a5087b87b',
        'X-Client-Secret': 'cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB'
    }
    response = requests.post(url, headers=headers, json={'retailUnit': 'ru'})
    return response.json()['access_token']

def get_token():
    file_destination = 'guest_token.txt'
    with open(file_destination, 'r') as file:
        content = file.readlines()
    if not content:
        with open(file_destination, 'w') as file:
            new_token = fetch_new_token()
            file.write(new_token)
        token = new_token
    else:
        token = content[0]
    return token

TOKEN = get_token()

CART_GRAPHQL = 'https://cart.oneweb.ingka.com/graphql'
CART_GRAPHQL_HEADERS = HEADERS
CART_GRAPHQL_HEADERS |= {
    'Host': 'cart.oneweb.ingka.com',
    'Authorization': 'Bearer ' + TOKEN,
    'X-Client-Id': '66e4684a-dbcb-499c-8639-a72fa50ac0c3'
}
CART_GRAPHQL_PROPS = ' {\n      ...CartProps\n    }\n  }\n  \n  fragment CartProps on Cart {\n    currency\n    checksum\n    context {\n      userId\n      isAnonymous\n      retailId\n    }\n    coupon {\n      code\n      validFrom\n      validTo\n      description\n    }\n    items {\n      ...ItemProps\n      product {\n        ...ProductProps\n      }\n    }\n    ...Totals\n  }\n  \nfragment ItemProps on Item {\n  itemNo\n  quantity\n  type\n  fees {\n    weee\n    eco\n  }\n  isFamilyItem\n  childItems {\n    itemNo\n  }\n  regularPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n      isLowerPrice\n      isTimeRestrictedOffer\n      previousPrice {\n        inclTax\n        exclTax\n        tax\n      }\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n  familyPrice {\n    unit {\n      inclTax\n      exclTax\n      tax\n      validFrom\n      validTo\n    }\n    subTotalExclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalInclDiscount {\n      inclTax\n      exclTax\n      tax\n    }\n    subTotalDiscount {\n      amount\n    }\n    discounts {\n      code\n      amount\n      description\n      kind\n    }\n  }\n}\n\n  \n  fragment ProductProps on Product {\n    name\n    globalName\n    isNew\n    category\n    description\n    isBreathTaking\n    formattedItemNo\n    displayUnit {\n      type\n      imperial {\n        unit\n        value\n      }\n      metric {\n        unit\n        value\n      }\n    }\n    measurements {\n      metric\n      imperial\n    }\n    technicalDetails {\n      labelUrl\n    }\n    images {\n      url\n      quality\n      width\n    }\n  }\n\n  \n  fragment Totals on Cart {\n    regularTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n    }\n    familyTotalPrice {\n      totalExclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalInclDiscount {\n        inclTax\n        exclTax\n        tax\n      }\n      totalDiscount {\n        amount\n      }\n      totalSavingsDetails {\n        familyDiscounts\n      }\n      totalSavingsInclDiscount {\n        amount\n      }\n    }\n  }\n\n\n'

def show_cart():
    data = {'query': '\n  query Cart(\n    $languageCode: String\n    ) '
            + '{\n    cart(languageCode: $languageCode) ' + CART_GRAPHQL_PROPS,
            'variables': {'languageCode': 'ru'}}
    request = requests.post(CART_GRAPHQL, headers=CART_GRAPHQL_HEADERS, json=data)
    return request.json()

def clear_cart():
    data = {'query':'\n  mutation ClearItems(\n    $languageCode: String\n  ) '
            + '{\n    clearItems(languageCode: $languageCode) ' + CART_GRAPHQL_PROPS,
            'variables': {'languageCode': 'ru'}}
    request = requests.post(CART_GRAPHQL, headers=CART_GRAPHQL_HEADERS, json=data)
    return request

def add_items_to_cart(items):
    items_templated = []
    for item in items:
        items_templated.append('{itemNo: "%s", quantity: %d}' % (item, items[item]))
    data = {'query':'mutation {addItems(items: ['
    + ', '.join(items_templated) + ']) {quantity}}'}
    request = requests.request('POST', CART_GRAPHQL, headers=CART_GRAPHQL_HEADERS, json=data)
    return request.json()

def delete_items_from_cart(items):
    items_str = []
    for item in items:
        items_str.append(str(item))
    data = {'query': '\n  mutation RemoveItems(\n    $itemNos: [ID!]!\n    $languageCode: String\n  )'
            + '{\n    removeItems(itemNos: $itemNos, languageCode: $languageCode) '
            + CART_GRAPHQL_PROPS,
            'variables': {
                'itemNos': items,
                'languageCode': 'ru'
            }}
    request = requests.post(CART_GRAPHQL, headers=CART_GRAPHQL_HEADERS, json=data)
    return request.json()

def fetch_delivery_options():
    headers = HEADERS
    headers |= {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN,
        'Host': 'ordercapture.ikea.ru',
        'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
    }
    endpoint = 'https://ordercapture.ikea.ru/ordercaptureapi/ru/checkouts'

    def get_checkout():
        data = {'shoppingType':'ONLINE','channel':'WEBAPP','checkoutType':'STANDARD',
        'languageCode':'ru','preferredServiceType':None,'requestedServiceTypes':None}
        request = requests.post(endpoint, headers=headers, json=data, verify=False)
        try:
            res = request.json()['resourceId']
        except ValueError("Cart is empty or something's wrong:"):
            res = request.json()
        return res

    def get_delivery_area(checkout):
        url = '%s/%s/delivery-areas' % (endpoint, checkout)
        data = {'zipCode': ZIP_CODE, 'enableRangeOfDays': False}
        request = requests.post(url, headers=headers, json=data, verify=False)
        return request.json()['resourceId']

    def get_delivery_services():
        checkout = get_checkout()
        delivery_area = get_delivery_area(checkout)
        url = '%s/%s/delivery-areas/%s/delivery-services' % (endpoint, checkout, delivery_area)
        request = requests.get(url, headers=headers, verify=False)
        return request.json()

    return get_delivery_services()

class DeliveryOption:
    def __init__ (self, delivery_id, type, service_type=None,
    delivery_date=None, price=0, unavailable_items=[]):
        self.delivery_id = id
        self.type = type
        self.service_type = service_type
        self.delivery_date = delivery_date
        self.price = price
        self.unavailable_items = unavailable_items

    def print(self):
        print('%s, %s, %s, %s, %d\nUnavailable items:' % (self.delivery_id,
        self.delivery_date, self.type, self.service_type, self.price))
        print(self.unavailable_items)

def format_delivery_date(from_date_time, to_date_time):
    date_re = re.compile(r'(20\d{2})-(\d{2})-(\d{2}).(\d{2}):(\d{2})')
    arr = []
    for date in from_date_time, to_date_time:
        new = date_re.search(date)
        arr.append('%s.%s.%s %s:%s' % (new[3], new[2], new[1], new[4], new[5]))
    if arr[0][:10] == arr[1][:10]:
        result = '%s–%s' % (arr[0], arr[1][11:])
    elif arr[0] == arr[1]:
        result = arr[0]
    else:
        result = '%s — %s' % (arr[0], arr[1])
    return result

def parse_delivery_options(options):
    parsed_options = []
    if options.get('errorCode'):
        raise Exception(options['message'])
    for option in options:
        try:
            price = option['servicePrice']['amount']
            price = int(re.search(r'(\d+)(.00)?', price)[1])
            date_info = option['deliveries'][0]['selectedTimeWindow']
            delivery_date = format_delivery_date(date_info['fromDateTime'],
                                                 date_info['toDateTime'])
        except:
            pass

        try:
            unavailable_items = []
            for item in option['unavailableItems']:
                unavailable_items.append({
                    'item_no': item['itemNo'],
                    'is_combination': item['type'] != 'ART',
                    'required_qty': item['requiredQuantity'],
                    'available_qty': item['availableQuantity']
                })
        except:
            unavailable_items = []

        parsed_option = DeliveryOption(
            option[id], option['fulfillmentMethodType'],
            option['servicetype'], delivery_date, price,
            unavailable_items
        )
        parsed_options.append(parsed_option)
    return parsed_options

def get_delivery_options():
    src = fetch_delivery_options()
    return parse_delivery_options(src)

def read_pass():
    with open("config.json", "r") as file:
        config = json.loads(file.read())
        return config['username'], config['password']

def login():
    with open("config.json", "r") as file:
        config = json.loads(file.read())
        usr = config['username']
        pswd = config['password']

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
    }

    # 1. /autorize  Autorize; redirects to /login with useful info
    code_verifier = generate_token(48)
    code_challenge = create_s256_code_challenge(code_verifier)
    state = generate_token(48)
    new_session_endpoint = 'https://ru.accounts.ikea.com/authorize?client_id=72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl&redirect_uri=https%3A%2F%2Fwww.ikea.com%2Fru%2Fru%2Fprofile%2Flogin%2F&response_type=code&ui_locales=ru-RU&' \
        + 'code_chalenge=' + code_challenge + '&code_chalenge_method=S256' \
        + '&scope=openid%20profile%20email&audience=https%3A%2F%2Fretail.api.ikea.com&registration=%7B%22bveventid%22%3Anull%7D&consumer=OWF&' \
        + 'state=' + state + '&auth0Client=eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0%3D'
    new_session_headers = headers
    new_session_headers['Accept']: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    new_login_response = session.get(new_session_endpoint, headers=new_session_headers)
    soup = BeautifulSoup(new_login_response.text, 'html.parser')
    encoded_config = soup.find('script', id='a0-config').get('data-config')
    decoded_config = base64.b64decode(encoded_config)
    session_config = json.loads(decoded_config)
    
    # 2. /usernamepassword/login    Log in system
    login_endpoint = 'https://ru.accounts.ikea.com/usernamepassword/login'
    login_payload = {
        'client_id': session_config['clientID'],
        'redirect_uri': session_config['callbackURL'],
        'tenant': session_config['auth0Tenant'],
        'response_type': session_config['extraParams']['response_type'],
        'scope': session_config['extraParams']['scope'],
        'audience': session_config['extraParams']['audience'],
        '_csrf': session_config['extraParams']['_csrf'],
        'state': session_config['extraParams']['state'],
        '_intstate': session_config['extraParams']['_intstate'],
        'username': usr,
        'password': pswd,
        'connection': 'Username-Password-Authentication'
    }
    login_headers = headers
    login_headers |= {
        'Referer': new_login_response.url,
        'Connection': 'keep-alive',
        'Auth0-Client': session_config['extraParams']['auth0Client'],
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-us',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    }
    login_result = session.post(login_endpoint, headers=login_headers, json=login_payload)

    # 3. /login/callback    Get code parameter from callback
    soup_1 = BeautifulSoup(login_result.text, 'html.parser')
    wctx = soup_1.find('input', {'name':'wctx'}).get('value')
    wresult = soup_1.find('input', {'name':'wresult'}).get('value')

    login_callback_endpoint = 'https://ru.accounts.ikea.com/login/callback'
    login_callback_headers = headers
    login_callback_headers |= {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ru.accounts.ikea.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': login_result.url,
        'Accept-Language': 'en-us'
    }
    login_callback_payload = 'wa=wsignin1.0&wresult=%s&wctx=%s' % (wresult, wctx)
    login_callback_response = session.post(login_callback_endpoint, headers=login_callback_headers, data=login_callback_payload)

    # 4. /oauth/token   Get access token
    token_enpoint = 'https://ru.accounts.ikea.com/oauth/token'
    token_headers = headers
    token_headers |= {
        'Content-Type': 'application/json',
        'Origin': 'https://www.ikea.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Referer': login_callback_response.url,
        'Accept-Language': 'en-us'
    }
    token_payload = {
        'grant_type': 'authorization_code',
        'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
        'code_verifier': code_verifier,
        'code': re.search(r'code=([^"&]+)', login_callback_response.url)[1],
        'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
        'scope': 'openid profile email'
    }
    token_response = session.post(token_enpoint, headers=token_headers, json=token_payload)
    token = token_response.json()['access_token']
    return token