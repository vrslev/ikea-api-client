from ...constants import Constants
from ...utils import get_config_values
from . import ItemFetchError, generic_item_fetcher


config = get_config_values()
country_code, language_code = config['country_code'], config['language_code']


def _fetch_items_specs(session, items: list) -> dict:
    url = 'https://api.ingka.ikea.com/salesitem/communications/{0}/{1}'.format(
        country_code, language_code)
    params = {'itemNos': ','.join(items)}
    response = session.get(url, params=params)
    r_json = response.json()
    if not 'data' in r_json and 'error' in r_json:
        err_msg = None
        if 'message' in r_json['error']:
            error = r_json['error']
            r_err_msg = error['message']
            if r_err_msg == 'no item numbers were found':
                try:
                    err_msg = error['details'][0]['value']['keys']
                except (KeyError, TypeError):
                    pass
            if not err_msg:
                err_msg = r_err_msg
        else:
            err_msg = r_json['error']
        raise ItemFetchError(err_msg)

    return r_json


def fetch(items):
    headers = {
        'Accept': '*/*',
        'Referer': '{0}/{1}/{2}/order/delivery/'.format(Constants.BASE_URL, country_code, language_code),
        'x-client-id': 'c4faceb6-0598-44a2-bae4-2c02f4019d06'
    }
    return generic_item_fetcher(items, headers, _fetch_items_specs, 50)
