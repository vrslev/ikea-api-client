from requests import Session
from ..utils import parse_item_code
from ..api import USER_AGENT


class ItemFetchError(Exception):
    pass


class WrongItemCodeError(Exception):
    pass


def _build_url(items: dict):
    endpoint = 'https://iows.ikea.com/retail/iows/ru/ru/catalog/items/'
    templated_list = []
    for item in items:
        templated_list.append('{0},{1}'.format(items[item], item))
    return endpoint + ';'.join(templated_list)


def _fetch_items_specs(input_items: list):
    session = Session()
    session.headers.update({
        'Accept': 'application/vnd.ikea.iows+json;version=2.0',
        'Origin': 'https://www.ikea.com',
        'Referer': 'https://www.ikea.com/ru/ru/shoppinglist/',
        'Cache-Control': 'no-cache, no-store',
        'Host': 'iows.ikea.com',
        'Accept-Language': 'ru',
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'consumer': 'MAMMUT#ShoppingList',
        'contract': '37249'
    })

    if len(input_items) == 0:
        return
    items = {}
    for item in input_items:
        items[item] = 'ART'

    for i in range(3):
        url = _build_url(items)
        response = session.get(url)
        if i == 0 and len(items) == 1 and not response.ok:
            items[item] = 'SPR'
            url = _build_url(items)
            response = session.get(url)
            if not response.ok:
                raise WrongItemCodeError(input_items[0])

        r_json = response.json()

        if 'RetailItemCommList' in r_json:
            if 'RetailItemComm' in r_json['RetailItemCommList']:
                return r_json['RetailItemCommList']['RetailItemComm']
            else:
                raise ItemFetchError(r_json)

        elif 'RetailItemComm' in r_json:
            return [r_json['RetailItemComm']]

        elif 'ErrorList' in r_json:
            errors = r_json['ErrorList']['Error']
            if not isinstance(errors, list):
                errors = [errors]

            for err in errors:
                for test in [
                    'ErrorCode' in err,
                    err['ErrorCode']['$'] == 1101,
                    'ErrorMessage' in err,
                    'ErrorAttributeList' in err,
                    'ErrorAttribute' in err['ErrorAttributeList']
                ]:
                    if not test:
                        raise ItemFetchError(err, test)

                attrs = {}
                for attr in err['ErrorAttributeList']['ErrorAttribute']:
                    attrs[attr['Name']['$']] = attr['Value']['$']
                item_code = str(attrs['ITEM_NO'])
                item_type = attrs['ITEM_TYPE']

                if i == 0:
                    items[item_code] = 'SPR' if item_type == 'ART' else 'ART'
                elif i == 1:
                    items.pop(item_code)


def fetch_items_specs(input_items):
    if isinstance(input_items, str):
        input_items = [input_items]
    elif not isinstance(input_items, list):
        raise TypeError('String or list required')

    input_items = list(set(input_items))
    input_items = parse_item_code(input_items)

    chunks = [input_items[x:x+90] for x in range(0, len(input_items), 90)]
    responses = []
    for chunk in chunks:
        response = _fetch_items_specs(chunk)
        responses += response
    return responses
