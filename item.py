import requests
import json

def return_response(response, is_list):
    if is_list:
        return response['RetailItemCommList']['RetailItemComm']
    else:
        return [response['RetailItemComm']]

def fetch_items_specs(items):
    endpoint = 'https://iows.ikea.com/retail/iows/ru/ru/catalog/items/'
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

    if type(items) is list:
        is_list = True
    else:
        is_list = False
        items = [items]

    items_templated = []
    for item in items:
        items_templated.append('ART,' + item)
    items_str = ';'.join(items_templated)

    # 1. Get data, catch errors
    url = endpoint + items_str
    response = session.get(url, headers=headers)
    response_res = response.json()
    if response.status_code == 404:
        raise ValueError('Wrong item code')
    try:
        return return_response(response_res, is_list)
    except KeyError:
        # 2. If error than some items are SPRs. Finding out which ones
        errors = response_res['ErrorList']['Error']
        if type(errors) is not list:
            errors = [errors]
        repaired_str = items_str
        for error in errors:
            item_code = str(error['ErrorAttributeList']['ErrorAttribute'][0]['Value']['$'])
            item_type = error['ErrorAttributeList']['ErrorAttribute'][1]['Value']['$']
            item_templated = '%s,%s' % (item_type, item_code)
            item_replacement = '%s,%s' % ('SPR' if item_type == 'ART' else 'ART', item_code)
            repaired_str = repaired_str.replace(item_templated, item_replacement)
        repaired_url = endpoint + repaired_str
        repaired_response = session.get(repaired_url, headers=headers)
        repaired_response_res = repaired_response.json()
        try:
            return return_response(repaired_response_res, is_list)
        except KeyError:
            # 3. If item is not ART nor SPR it means there's no such item. Deleting such items
            errors = repaired_response_res['ErrorList']['Error']
            final_str = repaired_str
            for err in errors:
                final_str = final_str.replace('%s,%s;' % (err['ErrorAttributeList']['ErrorAttribute'][1]['Value']['$'],
                str(err['ErrorAttributeList']['ErrorAttribute'][0]['Value']['$'])), '')
            final_url = endpoint + final_str
            final_response = session.get(final_url, headers=headers)
            final_response_res = final_response.json()
            return return_response(final_response_res, is_list)