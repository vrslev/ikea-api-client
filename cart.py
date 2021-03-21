import string
import random
import re
import json
import base64
import requests
import hashlib
from bs4 import BeautifulSoup

def read_config():
    file_name = 'config.json'
    try:
        open(file_name, 'x')
    except FileExistsError:
        pass
    with open(file_name, 'r+') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            json.dump({"username": "", "password": "", "zip_code": ""}, f)

CONFIG = read_config()
BASE_HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Origin': 'https://www.ikea.com',
    'Referer': 'https://www.ikea.com/'
}

def get_guest_token():
    url = 'https://api.ingka.ikea.com/guest/token'
    headers = BASE_HEADERS
    headers.update({
        'Host': 'api.ingka.ikea.com',
        'X-Client-Id': 'e026b58d-dd69-425f-a67f-1e9a5087b87b',
        'X-Client-Secret': 'cP0vA4hJ4gD8kO3vX3fP2nE6xT7pT3oH0gC5gX6yB4cY7oR5mB'
    })
    response = requests.post(url, headers=headers, json={'retailUnit': 'ru'})
    token = response.json()['access_token']
    return token

def create_s256_code_challenge(code_verifier):
    """
    https://github.com/lepture/authlib
    Create S256 code_challenge with the given code_verifier.
    """
    data = hashlib.sha256(bytes(code_verifier.encode('ascii', 'strict'))).digest()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8', 'strict')

def generate_token():
    """https://github.com/lepture/authlib"""
    rand = random.SystemRandom()
    return ''.join(rand.choice(string.ascii_letters + string.digits) for _ in range(48))

def get_authorized_token():
    """
    OAuth2 authorization
    """
    username = CONFIG['username']
    password = CONFIG['password']
    if not username and not password:
        raise Exception('Add username and password in config.json')

    session = requests.Session()
    headers = {
        'User-Agent': BASE_HEADERS['User-Agent']
    }

    # 1. /autorize  Autorize; redirects to /login with useful info
    code_verifier = generate_token()
    code_challenge = create_s256_code_challenge(code_verifier)
    state = generate_token()
    authorize_endpoint = 'https://ru.accounts.ikea.com/authorize?' \
        + 'client_id=72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl' \
        + '&redirect_uri=https%3A%2F%2Fwww.ikea.com%2Fru%2Fru%2Fprofile%2Flogin%2F' \
        + '&response_type=code' \
        + '&ui_locales=ru-RU' \
        + '&code_chalenge=' + code_challenge + '&code_chalenge_method=S256' \
        + '&scope=openid%20profile%20email' \
        + '&audience=https%3A%2F%2Fretail.api.ikea.com&registration=%7B%22bveventid%22%3Anull%7D' \
        + '&consumer=OWF' \
        + '&state=' + state + '&auth0Client=eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xNC4zIn0%3D'
    authorize_headers = headers
    authorize_headers['Accept']: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    authorize_response = session.get(authorize_endpoint, headers=authorize_headers)
    encoded_session_config = BeautifulSoup(authorize_response.text, 'html.parser').find('script', id='a0-config').get('data-config')
    session_config = json.loads(base64.b64decode(encoded_session_config))
    # 2. /usernamepassword/login    Log in system
    usrpwd_login_endpoint = 'https://ru.accounts.ikea.com/usernamepassword/login'
    usrpwd_login_payload = {
        'client_id': session_config['clientID'],
        'redirect_uri': session_config['callbackURL'],
        'tenant': session_config['auth0Tenant'],
        'response_type': session_config['extraParams']['response_type'],
        'scope': session_config['extraParams']['scope'],
        'audience': session_config['extraParams']['audience'],
        '_csrf': session_config['extraParams']['_csrf'],
        'state': session_config['extraParams']['state'],
        '_intstate': session_config['extraParams']['_intstate'],
        'username': username,
        'password': password,
        'connection': 'Username-Password-Authentication'
    }
    usrpwd_login_headers = headers
    usrpwd_login_headers.update({
        'Referer': authorize_response.url,
        'Connection': 'keep-alive',
        'Auth0-Client': session_config['extraParams']['auth0Client'],
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-us',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8.'
    })
    usrpwd_login_result = session.post(usrpwd_login_endpoint, headers=usrpwd_login_headers, json=usrpwd_login_payload)
    if not usrpwd_login_result.ok:
        raise Exception(usrpwd_login_result.json())

    # 3. /login/callback    Get code parameter from callback
    soup = BeautifulSoup(usrpwd_login_result.text, 'html.parser')
    wctx = soup.find('input', {'name':'wctx'}).get('value')
    wresult = soup.find('input', {'name':'wresult'}).get('value')

    login_callback_endpoint = 'https://ru.accounts.ikea.com/login/callback'
    login_callback_headers = headers
    login_callback_headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ru.accounts.ikea.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': usrpwd_login_result.url,
        'Accept-Language': 'en-us'
    })
    login_callback_payload = 'wa=wsignin1.0&wresult=%s&wctx=%s' % (wresult, wctx)
    login_callback_response = session.post(login_callback_endpoint, headers=login_callback_headers, data=login_callback_payload)

    # 4. /oauth/token   Get access token
    oauth_token_enpoint = 'https://ru.accounts.ikea.com/oauth/token'
    oauth_token_headers = headers
    oauth_token_headers.update({
        'Content-Type': 'application/json',
        'Origin': 'https://www.ikea.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Referer': login_callback_response.url,
        'Accept-Language': 'en-us'
    })
    oauth_token_payload = {
        'grant_type': 'authorization_code',
        'client_id': '72m2pdyUAg9uLiRSl4c4b0b2tkVivhZl',
        'code_verifier': code_verifier,
        'code': re.search(r'code=([^"&]+)', login_callback_response.url)[1],
        'redirect_uri': 'https://www.ikea.com/ru/ru/profile/login/',
        'scope': 'openid profile email'
    }
    oauth_token_response = session.post(
        oauth_token_enpoint,
        headers=oauth_token_headers,
        json=oauth_token_payload)
    token = oauth_token_response.json()['access_token']
    return token

class Cart:
    """
    Can show, clear a cart, add or delete items, get delivery options.
    """
    def __init__(self, use_authorized_token=False):
        file_name = 'storage.json'
        try:
            open(file_name, 'x')
        except FileExistsError:
            pass
        with open(file_name, 'r+') as f:
            try:
                storage = json.load(f)
            except json.decoder.JSONDecodeError:
                storage = {'guest_token': '', 'authorized_token': ''}
            if use_authorized_token:
                if not storage['authorized_token']:
                    storage['authorized_token'] = get_authorized_token()
                    f.seek(0)
                    f.truncate()
                    json.dump(storage, f)   
                token = storage['authorized_token']
            else:
                if not storage['guest_token']:
                    storage['guest_token'] = get_guest_token()
                    f.seek(0)
                    f.truncate()
                    json.dump(storage, f)
                token = storage['guest_token']

        self.token = token
        self.endpoint = 'https://cart.oneweb.ingka.com/graphql'
        self.headers = BASE_HEADERS
        self.headers.update({
            'Host': 'cart.oneweb.ingka.com',
            'Authorization': 'Bearer ' + token,
            'X-Client-Id': '66e4684a-dbcb-499c-8639-a72fa50ac0c3'
        })
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
        headers = BASE_HEADERS
        headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token,
            'Host': 'ordercapture.ikea.ru',
            'X-Client-Id': 'af2525c3-1779-49be-8d7d-adf32cac1934'
        })
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
        