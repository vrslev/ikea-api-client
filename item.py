import json
import requests

ITEMS_ENDPOINT = 'https://iows.ikea.com/retail/iows/ru/ru/catalog/items/'


def build_url(items):
    templated_list = []
    for item in items:
        templated_list.append('{0},{1}'.format(items[item], item))
    return ITEMS_ENDPOINT + ';'.join(templated_list)


def return_response(response, is_list):
    if is_list:
        return response['RetailItemCommList']['RetailItemComm']
    else:
        return [response['RetailItemComm']]


def _fetch_items_specs(input_items):
    headers = {
        'Accept': 'application/vnd.ikea.iows+json;version=2.0',
        'Origin': 'https://www.ikea.com',
        'Referer': 'https://www.ikea.com/ru/ru/shoppinglist/',
        'Cache-Control': 'no-cache, no-store',
        'Host': 'iows.ikea.com',
        'Accept-Language': 'ru',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'consumer': 'MAMMUT#ShoppingList',
        'contract': '37249'
    }
    session = requests.Session()

    if type(input_items) is list:
        is_list = False if len(input_items) == 1 else True
    else:
        is_list = False
        input_items = [input_items]

    items = {}
    for item in input_items:
        items[item] = 'ART'

    # 1. Get data, catch errors
    url = build_url(items)
    response = session.get(url, headers=headers)
    if response.status_code != 404:
        response_res = response.json()
    else:
        # If 404 and only one item is being fetched
        # then it's probably SPR
        if len(items) == 1:
            items[item] = 'SPR'
            url = build_url(items)
            response = session.get(url, headers=headers)
            if response.status_code == 404:
                raise ValueError('Wrong item code')
            else:
                response_res = response.json()
                

    try:
        return return_response(response_res, is_list)
    except (KeyError, json.decoder.JSONDecodeError):
        # 2. If error than some items are SPRs. Finding out which ones
        errors = response_res['ErrorList']['Error']
        if type(errors) is not list:
            errors = [errors]
        for error in errors:
            item_code = str(error['ErrorAttributeList']
                            ['ErrorAttribute'][0]['Value']['$'])
            item_type = error['ErrorAttributeList']['ErrorAttribute'][1]['Value']['$']
            items[item_code] = 'SPR' if item_type == 'ART' else 'ART'
        repaired_url = build_url(items)
        repaired_response = session.get(repaired_url, headers=headers)

        repaired_response_res = repaired_response.json()

        try:
            return return_response(repaired_response_res, is_list)
        except KeyError:
            # 3. If item is not ART nor SPR it means there's no such item. Deleting such items
            errors = repaired_response_res['ErrorList']['Error']
            if not type(errors) is list:
                errors = [errors]
            for err in errors:
                item_code = str(err['ErrorAttributeList']
                                ['ErrorAttribute'][0]['Value']['$'])
                item_type = err['ErrorAttributeList']['ErrorAttribute'][1]['Value']['$']
                items.pop(item_code)
            if len(items) == 1:
                is_list = False
            final_url = build_url(items)
            final_response = session.get(final_url, headers=headers)
            final_response_res = final_response.json()
            return return_response(final_response_res, is_list)


def fetch_items_specs(input_items):
    input_items = list(set(input_items))
    chunks = [input_items[x:x+90] for x in range(0, len(input_items), 90)]
    responses = []
    for chunk in chunks:
        response = _fetch_items_specs(chunk)
        responses += response
    return responses
